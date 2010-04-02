import os.path

from copy import deepcopy
from audiobatch.model import album
import types


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


class TrackInfo( object ):
    def __init__( self ):
        self.artists = []
        self.title = None
        self.track_number = None
        self.composers = []
        self.release_date = None
        self.genre = None
        self.isrc = None
        self.album_info = album.AlbumInfo()

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None

    def get_tag( self, tag_name ):
        """ The "tag" accessors provide string based access to a
        tracks information.  This is a convenience for configuring
        access with strings, say in a config file or dictionary, and
        and restricting access to only those attributes that are
        tags.""" 
        info_obj, tag_name = self._which( tag_name )
        return info_obj.__dict__[ tag_name ]

    def get_tag_unicode( self, tag_name ):
        """ Unicode is standard for audio file tag encoding. """
        val = self.get_tag( tag_name )
        if type(val) == types.ListType:
            return [unicode(x) for x in val]
        else:
            return unicode( val )
        
    def set_tag( self, tag_name, tag_val ):
        info_obj, tag_name = self._which( tag_name )
        info_obj.__dict__[ tag_name ] = tag_val

    def has_tag( self, tag_name ):
        is_multi = self.is_multi_value( tag_name )
        info_obj, tag_name = self._which( tag_name )
        val = info_obj.__dict__[ tag_name ]
        return ( ( is_multi and len(val) > 0 )
                 or ( not is_multi and val != None ) )

    def tags( self ):
        tag_names = self.__dict__.keys()
        tag_names.remove( "album_info" )
        album_tag_names = \
            [ ("album." + k) for k in self.album_info.__dict__.keys() ]
        tag_names.extend( album_tag_names )
        tags = {}
        for tag_name in tag_names:
            if self.has_tag( tag_name ):
                tags[ tag_name ] = self.get_tag( tag_name )
        return tags

    def is_empty( self ):
        return len( self.tags() ) == 0

    def _assert_is_track_tag( self, tag_name ):
        if tag_name == "album_info":
            raise AttributeError, "'album_info' not a track tag"
        elif tag_name not in self.__dict__:
            raise AttributeError, "'%s' not a track tag" % tag_name

    def is_multi_value( self, tag_name ):
        # FIXME should be staticly determinable
        info_obj, tag_name = self._which( tag_name )
        val = info_obj.__dict__[ tag_name ]
        return ( type(val) == types.ListType
                 or type(val) == types.DictType )
                     
    def _which( self, tag_name ):
        if tag_name.startswith("album."):
            return self.album_info, tag_name.split('.')[1]
        else:
            self._assert_is_track_tag( tag_name )
            return self, tag_name

