import os
import stat
import fnmatch
import logging
import shutil

import meta.generic

_LOGGER = logging.getLogger()

def _strip_extension( path ):
    return os.path.splitext( path )[0]
    
def match_extensions( relative_paths, extensions ):
    patterns = set()
    for ext in extensions:
        patterns.add('*' + os.extsep + ext)

    matches = []
    for rel_path in relative_paths:
        for pattern in patterns:
            if fnmatch.fnmatch(rel_path, pattern):
                matches.append( rel_path )
    return matches


def filter_audio_files( files_rel, dir_abs, pass_condition_template ):
    check_ext = False
    check_bitrate = False
    format_kwargs = {}
    if pass_condition_template.find( "{extension}" ) != -1:
        check_ext = True
        format_kwargs["extension"] = "ext"
    if pass_condition_template.find( "{bitrate}" ) != -1:
        check_bitrate = True
        format_kwargs["bitrate"] = "bitrate"

    pass_condition = pass_condition_template.format( **format_kwargs )

    passes = []
    rejects = []

    for file_rel in files_rel:
        if check_ext:
            # ext is "unused" -- only referenced within eval
            # pylint: disable-msg=W0612
            ext = _strip_extension( file_rel )
        if check_bitrate:
            file_abs = os.path.join( dir_abs, file_rel )
            audio_file = meta.generic.read_audio_file( file_abs )
            # bitrate is "unused" -- only referenced within eval
            # pylint: disable-msg=W0612
            bitrate = int( audio_file.bitrate / 1000 )
        if eval ( pass_condition ):
            passes.append( file_rel )
        else:
            rejects.append( file_rel )
        
    return passes, rejects


def _should_exclude( path, exclude_patterns ):
    if exclude_patterns == None or len(exclude_patterns) == 0:
        return False

    for exclude_pat in exclude_patterns:
        if fnmatch.fnmatch( path, exclude_pat ):
            return True

    return False


def find_paths( base_dir_abs,
                extensions=None,
                exclude_patterns=None,
                return_rel_path=True):

    paths = set()
    for path, _, files in os.walk(base_dir_abs):
        for name in files:
            patterns = []
            if extensions == None:
                patterns.append('*')
            else:
                for ext in extensions:
                    patterns.append('*' + os.extsep + ext)
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    absolute_path = os.path.join(path, name)
                    if not _should_exclude( absolute_path, exclude_patterns ):
                        if return_rel_path:
                            paths.add( os.path.relpath( absolute_path,
                                                        base_dir_abs ) )
                        else:
                            paths.add( absolute_path )
                    break

    return paths

def convert_paths( source_dir_abs,
                   sources_rel,
                   target_dir_abs,
                   stream_converter,
                   meta_converter ):
    i = 0
    for source_rel in sources_rel:
        i += 1
        _LOGGER.debug( "Converting %d of %d: %s" \
                           % (i, len( sources_rel ), source_rel) )
        source_abs = os.path.join( source_dir_abs, source_rel )
        target_rel = _strip_extension( source_rel ) + os.extsep + "mp3"
        target_abs = os.path.join( target_dir_abs, target_rel )
        try:
            stream_converter.convert( source_abs, target_abs )
            stream_conversion_error = None
        # We want to be able to continue processing the batch of paths
        # no matter what error ocurrs on a particular file.
        # pylint: disable-msg=W0703
        except Exception as ex:
            stream_conversion_error = ex
        try:
            meta_converter.convert( source_abs, target_abs )
            meta_conversion_error = None
        # pylint: disable-msg=W0703
        except Exception as ex:
            meta_conversion_error = ex

        # We'll yield errors, instead of returning them all at the end,
        # so that the caller has control to stop processing due to errors
        yield source_rel, stream_conversion_error, meta_conversion_error


def copy_paths( source_dir_abs, paths_rel, target_dir_abs ):
    total_copies = len( paths_rel )
    i = 0
    for path_rel in paths_rel:
        i += 1
        source_path_abs = os.path.join( source_dir_abs, path_rel )
        target_path_abs = os.path.join( target_dir_abs, path_rel )
        _LOGGER.debug( "Copying %d of %d: %s" % (i, total_copies, path_rel) )
            
        target_leaf_dir = os.path.dirname( target_path_abs )
        if not os.path.isdir( target_leaf_dir ):
            os.makedirs( target_leaf_dir )
                    
        shutil.copyfile( source_path_abs, target_path_abs) 


def delete_paths( dir_abs, paths_rel ):
    for path_rel in paths_rel:
        path_abs = os.path.join( dir_abs, path_rel )
        _LOGGER.debug( "Deleting: %s" % path_abs )
        os.remove( path_abs )
        

def _has_been_updated( source_rel,
                       target_rel,
                       source_dir_abs,
                       target_dir_abs ):
    source_abs = os.path.join( source_dir_abs, source_rel )
    source_mod_time = os.stat( source_abs )[stat.ST_MTIME]

    target_abs = os.path.join( target_dir_abs, target_rel )
    target_mod_time = os.stat( target_abs )[stat.ST_MTIME]

    return source_mod_time > target_mod_time


def _strip_extensions( file_paths ):
    stripped = []
    for path in file_paths:
        # leaves the '.' on the end so that file sort order doesn't change
        stripped.append( _strip_extension(path) + os.extsep )            
    return stripped

# Determine all new sources, updated sources and matchless targets so that we
# can identify the tasks necessary to bring the target collection up to date
# with the source collection.  File conversion is assumed, so extensions are
# ignored in processing the diff.
#
# The function assumes only one file exists per title exists (e.g. file paths
# differ by more than just extension).  If this is not the case for some title,
# the function will ensure that at least one copy of the title remains or is
# scheduled for the targets.
#
# The function has a lot of local variables
def extension_ignorant_diff( sources, targets, source_dir_abs, target_dir_abs ):

    sources = sorted( sources )
    stripped_sources = _strip_extensions( sources )

    targets = sorted( targets )
    stripped_targets = _strip_extensions( targets )
    
    new_sources = []
    updated_sources = []
    matchless_targets = []
    num_sources = len( stripped_sources ) 
    num_targets = len( stripped_targets ) 
    s_idx = 0
    t_idx = 0
    target_matched = False

    # Two pointers, one for the sources and one for the targets, are walked
    # in tandem.  Since the sources and targets have been sorted, we can
    # diff the two lists in a single pass through both lists.
    while not (s_idx == num_sources and t_idx == num_targets):
        if s_idx == num_sources:
            if not target_matched:
                matchless_targets.append( targets[t_idx] )
            t_idx += 1
            target_matched = False
        elif t_idx == num_targets:
            new_sources.append( sources[s_idx] )
            s_idx += 1
        else:
            comparison = cmp( stripped_sources[s_idx],
                              stripped_targets[t_idx] )
            # This algorithm will not allow duplicate paths (with diff
            # extenson, only) to remain in the target folder.  The second
            # path encountered will be indicated as matchless.
            if comparison == 0:
                # Indicate the match so we don't delete the target on the
                # next loop
                target_matched = True
                if _has_been_updated( sources[s_idx],
                                      targets[t_idx],
                                      source_dir_abs,
                                      target_dir_abs ):
                    updated_sources.append( sources[s_idx] )
                s_idx += 1
            elif comparison < 0:
                assert(not target_matched)
                new_sources.append( sources[s_idx] )
                s_idx += 1
            elif comparison > 0:
                if not target_matched:
                    matchless_targets.append( targets[t_idx] )
                t_idx += 1
                target_matched = False
    
    return new_sources, updated_sources, matchless_targets

def update_meta( track_meta, paths_abs ):
    for path_abs in paths_abs:
        track_meta.writeFile( path_abs )
