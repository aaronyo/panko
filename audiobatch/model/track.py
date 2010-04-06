import os.path
import UserDict
from types import ListType, DictType, IntType

from copy import deepcopy
import types

from audiobatch.model import _info


def extless_compare( track1, track2 ):    
    return cmp( track1.extless_relative_path, track2.extless_relative_path )


class Track( object ):
    """ An implmentation of a 'Track' that loads content lazily. """
    def __init__( self, mod_time, library_dir, relative_path ):
        self.mod_time = mod_time
        self.library_dir = library_dir
        self.relative_path = relative_path

    def get_track_info( self ):
        raise NotImplementedError()

    def get_audio_stream( self ):
        raise NotImplementedError()

    @property
    def extless_relative_path( self ):
        extless, _ = os.path.splitext( self.relative_path )
        return extless

    @property
    def extension( self ):
        _, ext = os.path.splitext( self.relative_path )
        return ext


class LazyTrack( Track ):
    """ An implmentation of a 'Track' that loads content lazily. """
    def __init__( self, mod_time, library_dir, relative_path, track_repo ):
        Track.__init__( self, mod_time, library_dir, relative_path )
        self._track_repo = track_repo
        self._track_info = None
        self._audio_stream = None

    def get_track_info( self ):
        if self._track_info == None:
            self._track_info = \
                self._track_repo.get_track_info( self.library_dir,
                                                 self.relative_path)
        return deepcopy( self._track_info )

    def get_audio_stream( self ):
        if self._audio_stream == None:
            self._audio_stream = \
                self._track_repo.get_audio_stream( self.library_dir,
                                                   self.relative_path)
        # FIXME: use a flyweight for the actual stream/path within an
        # audio stream.  If a path gets moved, we want all existing
        # AudioStream instances to have their path ref updated.
        return deepcopy( self._audio_stream )

# FIXME: remove this once convinced that Track classes will be immutable.
#    def __deepcopy__(self, memo):
#        """ Overriding the standard deepcopy behavior because we don't
#        want our library, just used for lazy loading, to be deepcopied. """
#        dup = LazyTrack( self._library,
#                         deepcopy( self.library_key, memo ),
#                         deepcopy( self.mod_time, memo ) )
#        dup._track_info = deepcopy( self._track_info, memo )
#        dup._audio_stream = deepcopy( self._audio_stream, memo )
#        return dup


class TrackInfo( _info.Info ):
    def __init__( self, fields_dict = None ):
        _info.Info.__init__( self )
        self._add_field( "artists", ListType )
        self._add_field( "title" )
        self._add_field( "track_number", IntType )
        self._add_field( "track_total", IntType )
        self._add_field( "disc_number", IntType)
        self._add_field( "disc_total", IntType )
        self._add_field( "composers", ListType)
        self._add_field( "genres", ListType )
        self._add_field( "isrc" )
        if fields_dict != None: self.update( fields_dict )

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None




