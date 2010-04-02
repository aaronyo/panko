""" A module for supporting persistence of 'Tracks'

This module encapsulates all details of the file system and encoding.
It is the bridge between our abstract model and persistence.
For example, searching folders and the differences between id3 tags
and vorbis comments should be contained in or below this module.

classes:
TrackRespository -- does all the work

"""

import os.path
import fnmatch
import stat
import shutil

from audiobatch.util import cache
from audiobatch.model.track import LazyTrack
from audiobatch.persistence import audiofile

_repository = None
_DEFAULT_AUDIO_EXTENSIONS= ['mp3', 'flac', 'm4a']
_DEFAULT_EXCLUDE_PATTERNS= [".*", "*/.*"]

def init_repository( cache_size ):
    global _repository
    _repository = TrackRepository( cache_size,
                                   _DEFAULT_AUDIO_EXTENSIONS,
                                   _DEFAULT_EXCLUDE_PATTERNS )

def get_repository():
    global _repository
    if _repository == None:
        init_repository( 1000 )
    return _repository

class TrackRepository( object ):

    """ A class for retrieving and persisting 'Tracks' to/from the file system
    """

    def __init__( self, cache_size, extensions, exclude_patterns ):
        """ 'cache_size' specifies the number of audio_files to cache

        The motiviation behind the cache is to avoid round trips to the file
        system.  This is particularly effective when files are located
        across the network

        """
        # FIXME: I've seen at lease one bug where mutagen leaves a file
        # open, which means this cache would leave file descriptors open.
        # Does it make more sense to just cache Track instances?
        self._audio_file_cache = cache.LRUCache( cache_size )
        self._extensions = extensions
        self._exclude_patterns = exclude_patterns

    def all_tracks( self,
                    library_dir ):

        relative_paths = self._find_paths( library_dir,
                                           self._extensions,
                                           self._exclude_patterns )
        tracks = []
        for rel_path in relative_paths:
            abs_path = os.path.join( library_dir, rel_path )
            mod_time = os.stat( abs_path )[stat.ST_MTIME]
            # Paths is a set, which helps us enforce that our keys for the
            # audio tracks are unique
            track = LazyTrack( mod_time = mod_time,
                               library_dir = library_dir,
                               relative_path = rel_path,
                               track_repo = self )
            tracks.append( track )
              
        return tracks

    def filter_tracks( self,
                       library_dir,
                       filter ):
        tracks = self.all_tracks( library_dir )
        filtered_tracks = []
        for track in tracks:
            if filter( track ):
                filtered_tracks.append( track )

        return filtered_tracks

    def get_track_info( self, library_dir, track_path ):
        audio_file = self._get_audio_file( library_dir, track_path )
        return audio_file.get_track_info()
                                      
    def get_audio_stream( self, library_dir, track_path ):
        audio_file = self._get_audio_file( library_dir, track_path )
        return audio_file.get_audio_stream()

    def create( self,
                library_dir,
                track_path,
                track_info,
                audio_stream ):
        audio_file = audiofile.read( audio_stream.path )
        audio_file.update_track_info( track_info )
        audio_file.save()
        abs_track_path = os.path.join( library_dir, track_path )
        target_dir = os.path.dirname( abs_track_path )
        if not os.path.isdir( target_dir ):
            os.makedirs( target_dir )                
        shutil.move( audio_stream.path, abs_track_path )

    def update( self,
                library_dir,
                track_path,
                track_info = None,
                audio_stream = None ):
        if track_info == None and audio_stream == None:
            raise ValueError( "track_info or audio_stream must have value" )

        audio_file = self._get_audio_file( library_dir, track_path )
        if track_info != None:
            audio_file.update_track_info( track_info )
        if audio_stream != None:
            audio_file.set_audio_stream( audio_stream )
        audio_file.save()


    def update_track( self, track, track_info = None, audio_stream = None ):
        self.update( track.library_dir,
                     track.relative_path,
                     track_info,
                     audio_stream )


    def copy( self,
              source_dir,
              source_track_path,
              target_dir,
              target_track_path ):
        abs_source_path = os.path.join( source_dir, source_track_path ) 
        abs_target_path = os.path.join( target_dir, target_track_path ) 

        target_dir = os.path.dirname( abs_target_path )
        if not os.path.isdir( target_dir ):
            os.makedirs( target_dir )                
        shutil.copy2( abs_source_path, abs_target_path )


    def delete( self, library_dir, track_path ):
        self._del_audio_file( library_dir, track_path )


    def _find_paths( self,
                    base_dir_abs,
                    extensions=None,
                    exclude_patterns=None,
                    return_rel_path=True ):

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
                        if not TrackRepository._should_exclude(
                            absolute_path,
                            exclude_patterns ):
                            if return_rel_path:
                                paths.add( os.path.relpath( absolute_path,
                                                            base_dir_abs ) )
                            else:
                                paths.add( absolute_path )
                        break

        return paths

    def _get_audio_file( self, library_dir, track_path ):
        abs_path = os.path.join( library_dir, track_path )

        if abs_path not in self._audio_file_cache:
            self._audio_file_cache[ abs_path ] = audiofile.read( abs_path )

        return self._audio_file_cache[ abs_path ]

    def _del_audio_file( self, library_dir, track_path ):
        abs_path = os.path.join( library_dir, track_path )
        if abs_path in self._audio_file_cache:
            del self._audo_file_cache[ abs_path ]
        os.unlink( abs_path )

    @staticmethod
    def _should_exclude( path, exclude_patterns ):
        if exclude_patterns == None or len(exclude_patterns) == 0:
            return False

        for exclude_pat in exclude_patterns:
            if fnmatch.fnmatch( path, exclude_pat ):
                return True
        return False
