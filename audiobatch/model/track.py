import os.path
import UserDict
from collections import namedtuple
from types import ListType, DictType, IntType

from copy import deepcopy
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


_Field = namedtuple( "Field", "name, mandatory_type, value" )

class _FieldedObject( object ):
    def __init__( self ):
        self._fields = {}

    def __setattr__( self, name, val ):
        if name == "_fields":
            object.__setattr__( self, name, val )
            return

        if name in self._fields.keys():
            old_field = self._fields[ name ]
            self._fields[ name ] = old_field._replace( value = val )
        else:
            object.__setattr__( self, name, val )

    def __getattr__( self, name ):
        return self._fields[ name ].value

    def _add_field( self, name, mandatory_type = None ):
        self._fields[name] = _Field( name, mandatory_type, None)


class TrackInfo( _FieldedObject, UserDict.DictMixin ):
    def __init__( self ):
        _FieldedObject.__init__( self )
        self._add_field( "artists", ListType )
        self._add_field( "title" )
        self._add_field( "track_number", IntType )
        self._add_field( "track_total", IntType )
        self._add_field( "disc_number", IntType)
        self._add_field( "composers", ListType)
        self._add_field( "release_date")
        self._add_field( "genre" )
        self._add_field( "isrc" )
        self.album_info = AlbumInfo()

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None

    def keys( self ):
        field_keys = []
        for k, v in self._fields.items():
            if v.value != None:
                field_keys.append( k )
        for k, v in self.album_info._fields.items():
            if v.value != None:
                field_keys.append( "album." + k )
        return field_keys

    def __getitem__( self, key ):
        """ The dictionary accessors provide string based access to a
        tracks information.  This is a convenience for configuring
        access with strings, say in a config file or dictionary, and
        and restricting access to only those attributes that are
        tags.""" 
        info_obj, specific_key = self._which( key )
        val = info_obj._fields[ specific_key ].value
        if val == None:
            raise KeyError(key)
        else:
            return val

    def __setitem__( self, key, val ):
        info_obj, specific_key = self._which( key )
        old_field = info_obj._fields[ specific_key ]
        info_obj._fields[ specific_key ] = old_field._replace( value = val )

    def _assert_is_track_tag( self, tag_name ):
        if tag_name == "album_info":
            raise AttributeError, "'album_info' not a track tag"
        elif tag_name not in self.__dict__:
            raise AttributeError, "'%s' not a track tag" % tag_name

    def is_multi_value( self, key ):
        # FIXME should be staticly determinable
        info_obj, specific_key = self._which( key )
        field_type = info_obj._fields[ specific_key ].mandatory_type
        return ( field_type == types.ListType
                 or field_type == types.DictType )
    
    def is_int( self, key ):
        info_obj, specific_key = self._which( key )
        field_type = info_obj._fields[ specific_key ].mandatory_type
        return field_type == IntType

    def _which( self, tag_name ):
        if tag_name.startswith("album."):
            return self.album_info, tag_name.split('.')[1]
        else:
            return self, tag_name


class AlbumInfo( _FieldedObject ):
    def __init__( self ):
        _FieldedObject.__init__( self )
        self._add_field( "artists", ListType )
        self._add_field( "composers", ListType )
        self._add_field( "title" )
        self._add_field( "disc_total", IntType )
        self._add_field( "release_date" )
        self._add_field( "isrc" )
        # valid keys are described in the 'model.image' module
        self.images = {}
        self._add_field( "images", DictType )

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None
