import os
import os.path

from audiobatch.persistence import trackrepo
from audiobatch.model import track
from audiobatch.model import audiostream
from audiobatch.service import ServiceEvent
from audiobatch import service

def pass_all( track ): return True

def prepare_export( source_dir,
                    target_dir,
                    convert_test = pass_all,
                    copy_test = pass_all,
                    del_matchless_targets = False ):
    track_repo = trackrepo.get_repository()
    source_tracks = track_repo.find_tracks( source_dir )
    target_tracks = track_repo.find_tracks( target_dir )

    new_sources, updated_sources, matchless_targets = \
        _export_diff( source_tracks, target_tracks )

    export_job = ExportJob( source_dir, target_dir )
    for source in new_sources:
        if convert_test( source ):
            export_job.add_convert( source, True )
        elif copy_test (source):
            export_job.add_copy( source, True )
        else:
            export_job.add_ignore( source, True )
    for source in updated_sources:
        if convert_test( source ):
            export_job.add_convert( source, False )
        elif copy_test (source):
            export_job.add_copy( source, False )
        else:
            export_job.add_ignore( source, False )
    if del_matchless_targets:
        for t in matchless_targets: export_job.add_delete(t)

    return export_job

def export( export_job,
            convert_format,
            stream_converter = audiostream.make_converter(),
            listen = service.default_event_listener() ):

    track_repo = trackrepo.get_repository()

    num_converts = len( export_job.converts )
    num_copies = len( export_job.copies )
    num_deletes = len( export_job.deletes )
    i = 0
    for track, is_new in export_job.converts:
        i += 1
        listen( ExportTrackingEvent( "Converting",
                                     i,
                                     num_converts,
                                     track.relative_path,
                                     is_new ) )
        try:
            new_stream = stream_converter.convert( track.get_audio_stream(),
                                                   convert_format )
            target_rel_path =  ( track.extless_relative_path +
                                 os.extsep +
                                 audiostream.ext_for_format( convert_format ) )
            if is_new:
                track_repo.create( export_job.target_dir,
                                   target_rel_path,
                                   track.get_track_info(),
                                   new_stream )
            else:
                track_repo.update( export_job.target_dir,
                                   target_rel_path,
                                   track.get_track_info(),
                                   new_stream )
        except Exception as e:
            listen( ExportErrorEvent( "Converting",
                                      track.relative_path,
                                      e ) )

    i = 0
    for track, is_new in export_job.copies:
        i += 1
        listen( ExportTrackingEvent( "Copying",
                                     i,
                                     num_copies,
                                     track.relative_path,
                                     is_new ) )
        try:
            track_repo.copy( export_job.source_dir,
                             track.relative_path,
                             export_job.target_dir,
                             track.relative_path )
        except Exception as e:
            listen( ExportErrorEvent( "Copying",
                                      track.relative_path,
                                      e ) )

    # let's use a dif name for our iteration var here, just to help avoid
    # a bug where we delete the wrong thing
    i = 0
    for del_track in export_job.deletes:
        i += 1
        listen( ExportTrackingEvent( "Deleting",
                                     i,
                                     num_deletes,
                                     del_track.relative_path,
                                     is_new ) )
        try:
            track_repo.delete( export_job.target_dir,
                               del_track.relative_path )
        except Exception as e:
            listen( ExportErrorEvent( "Deleting",
                                      del_track.relative_path,
                                      e ) )


def _export_diff( sources, targets ):

    """
    Determine tasks necessary to bring the target collection up to date.

    Identify all new sources, updated sources and matchless targets.  File
    conversion is assumed, so extensions are ignored in processing the diff.

    The function assumes only one file exists per title (e.g. file paths
    differ by more than just extension).  If this is not the case for
    some title, the function will ensure that at least one copy of the
    title remains or is scheduled for the targets.
    """

    sources = sorted( sources, track.extless_compare )
    targets = sorted( targets, track.extless_compare )

    new_sources = []
    updated_sources = []
    matchless_targets = []
    num_sources = len( sources ) 
    num_targets = len( targets ) 
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
            comparison = track.extless_compare( sources[s_idx], targets[t_idx] )
            # This algorithm will not allow duplicate paths (with diff
            # extenson, only) to remain in the target folder.  The second
            # path encountered will be indicated as matchless.
            if comparison == 0:
                # Indicate the match so we don't delete the target on the
                # next loop
                target_matched = True
                if sources[s_idx].mod_time > targets[t_idx].mod_time:
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

    
class ExportJob( object ):
    def __init__( self, source_dir, target_dir ):
        self.source_dir = source_dir
        self.target_dir = target_dir
        self.ignores = []
        self.converts = []
        self.copies = []
        self.deletes = []

    def add_convert( self, track, is_new ):
        self.converts.append( (track, is_new) )

    def add_copy( self, track, is_new ):
        self.copies.append( (track, is_new) )

    def add_ignore( self, track, is_new ):
        self.ignores.append( (track, is_new) )

    def add_delete( self, track ):
        self.deletes.append( track )                

    def has_work( self ):
        return (    len( self.converts ) > 0
                 or len( self.copies ) > 0
                 or len( self.deletes ) > 0 )

    def summary( self ):
        copy_new = 0; copy_upd = 0;
        conv_new = 0; conv_upd = 0;
        ignr_new = 0; ignr_upd = 0;
        deletes = len(self.deletes)
        for x in self.copies:
            if x[1] == False: copy_upd += 1
            else: copy_new += 1 
        for x in self.converts:
            if x[1] == False: conv_upd += 1
            else: conv_new += 1 
        for x in self.ignores:
            if x[1] == False: ignr_upd += 1
            else: ignr_new += 1 

        str = "export from: %s to: %s\n" % ( self.source_dir, self.target_dir )
        str += "%d new files will be converted\n" % conv_new
        str += "%d new files will be copied\n" % copy_new
        str += "%d new files will be ignored\n" % ignr_new
        str += "%d updated files will be converted\n" % conv_upd
        str += "%d updated files will be copied\n" % copy_upd
        str += "%d updated files will be ignored\n" % ignr_upd
        str += "%d stale targets will be deleted" % deletes

        return str


class ExportTrackingEvent( ServiceEvent ):
    def __init__( self, type, num, total, rel_path, is_new ):
        ServiceEvent.__init__( self, ServiceEvent.INFO )
        self.type = type
        self.num = num
        self.total = total
        self.rel_path = rel_path
        self.is_new = is_new

    def get_message( self ):
        file_desc = "new" if self.is_new else "updated"
        file_desc = "stale target" if (self.type == "Deleting") else file_desc
        msg = "%s (%d/%d) %s file: '%s'" % ( self.type,
                                             self.num,
                                             self.total,
                                             file_desc,
                                             self.rel_path )
        return msg


class ExportErrorEvent( ServiceEvent ):
    def __init__( self, type, rel_path, exception ):
        ServiceEvent.__init__( self, ServiceEvent.ERROR )
        self.type = type
        self.rel_path = rel_path
        self.exception = exception

    def get_message( self ):
        msg = "%s '%s' failed: %s" % ( self.type,
                                       self.rel_path,
                                       self.exception )
        return msg
