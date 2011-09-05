import cPickle
import json
import os.path
import datetime

from audiobatch.model import track, album, audiostream, _info

_albms = {}
_trcks = []

def _make_persist_dir():
    home_dir = os.path.expanduser('~')
    return os.path.join(home_dir, '.audiobatch')

_persist_dir = _make_persist_dir()

_datetime_format = "%Y-%m-%d %H:%M:%S:%f"
def _decode_datetime( str_dt ):
    return datetime.datetime.strptime( str_dt, _datetime_format )

def _encode_datetime( obj_dt ):
    return obj_dt.strftime( _datetime_format )


def _track_to_dict( trck ):
    track_dict = {}
    track_dict["mod_time"] = trck.mod_time
    track_dict["base_dir"] = trck.base_dir
    track_dict["relative_path"] = trck.relative_path
    track_dict["track_info"] = dict( trck.get_track_info() )

    astream = trck.get_audio_stream()
    as_dict = {}
    as_dict["bitrate"] = astream.bitrate
    as_dict["format"] = astream.format
    as_dict["path"] = astream.path
    track_dict["audio_stream"] = as_dict

    return track_dict


def _album_to_dict( albm ):
    album_dict = {}
    album_dict["album_info"] = dict( albm.get_album_info() )
    album_dict["tracks"] = albm.get_tracks()

    return album_dict


def _album_from_dict( album_dict ):
    albm = album.DTOAlbum()
    ai = album.AlbumInfo()
    for k, v in album_dict["album_info"].items():
        if k == "release_date":
            ai[ k ] = _info.LenientDateTime.parse( v )
        else:
            ai[ k ] = v

    albm.set_album_info( ai )

    for trck in album_dict["tracks"]:
        albm.add_track( trck )

    return albm


def _track_from_dict( track_dict ):
    trck = track.DTOTrack( _decode_datetime( track_dict["mod_time"] ),
                           track_dict["base_dir"],
                           track_dict["relative_path"], )

    trck.set_track_info( track.TrackInfo( track_dict["track_info"] ) )

    as_dict = track_dict["audio_stream"]
    astream = audiostream.AudioStream( as_dict["bitrate"],
                                       as_dict["format"],
                                       as_dict["path"] )
    trck.set_audio_stream( astream )

    return trck
               
       
class TrackJSONEncoder( json.JSONEncoder ):
    def default( self, obj ):
        if isinstance( obj, track.Track ):
            return _track_to_dict( obj )
        elif isinstance( obj, _info.LenientDateTime ):
            return str( obj )
        elif isinstance( obj, datetime.datetime ):
            return _encode_datetime( obj )
        elif isinstance( obj, album.Album ):
            return _album_to_dict( obj )
        else:
            raise TypeError

_jsonenc = TrackJSONEncoder()

def _object_hook( dct ):
    if "track_info" in dct:
        return _track_from_dict( dct )
    elif "album_info" in dct:
        return _album_from_dict( dct )
    else:
        return dct

def _library_path( library_name ):
    return os.path.join( _persist_dir, library_name )

def _albums_path( library_name ):
    return os.path.join( _library_path( library_name ), "albums" )

def _watch_folders_path( library_name ):
    return os.path.join( _library_path( library_name ), "watch" )


class LibDB:
    def __init__( self, library_name ):
        self.library_name = library_name
        if not os.path.exists( _library_path( self.library_name ) ):
            os.makedirs( _library_path( self.library_name ) )
    
    def save_album( self, albm ):
        libfile = open( _albums_path( self.library_name ), "w" )
        _albms[ albm.id ] = albm
        json.dump( _albms.values(),
                   libfile,
                   default = _jsonenc.default, 
                   sort_keys = True,
                   indent = 4)
        libfile.close()

    def load_albums( self ):
        libfile = open( _albums_path( self.library_name ), "r" )
        albms = json.load( libfile, object_hook=_object_hook )
        libfile.close()
        return albms

    def save_track( self, trck ):
        libfile = open( _albums_path( self.library_name ), "w" )
        json.dump( trck,
                   libfile,
                   default = _jsonenc.default, 
                   sort_keys = True,
                   indent = 4)
        libfile.close()

    def load_tracks( self ):
        libfile = open( _albums_path( self.library_name ), "r" )
        trck = json.load( libfile, object_hook=_object_hook )
        libfile.close()
        return trck

    def delete_library( self ):
        if os.path.exists( _albums_path( self.library_name ) ):
            os.unlink( _albums_path( self.library_name ) )
        if os.path.exists( _watch_folders_path( self.library_name ) ):
            os.unlink( _watch_folders_path( self.library_name ) )
        os.rmdir( _library_path( self.library_name ) )
        _albms.clear()
        del _trcks[:]

    def save_watch_folder( self, path):
        folders = self.load_watch_folders()

        if path not in folders:
            folders.append( path )

        watchfile = open( _watch_folders_path( self.library_name ), "w" )
        json.dump( folders, watchfile, sort_keys = True, indent = 4)
        watchfile.close()

    def load_watch_folders( self ):
        if os.path.exists( _watch_folders_path( self.library_name ) ):
            watchfile = open( _watch_folders_path( self.library_name ), "r" )
            folders = json.load( watchfile )
            watchfile.close()
            return folders
        else:
            return []
        
