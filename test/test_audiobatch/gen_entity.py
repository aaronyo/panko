import os.path
import datetime
import string

from audiobatch.model import track, album, audiostream, format
from test_audiobatch import gen_info

_DUMMY_LIB_DIR = "/tmp/test_lib_dir"
_DUMMY_EXT = "mp3"

_NUM_ALBUM_TRACKS = 7

def random_track():
    base_dir, rel_path = gen_info.random_temp_mp3_path()
    trck = track.DTOTrack( datetime.datetime.now(), base_dir, rel_path )
    ti = gen_info.random_track_info()
    trck.set_track_info( ti )
    audstrm = audiostream.AudioStream( 128000,
                                  format.MP3_STREAM,
                                  os.path.join( base_dir, rel_path ) )
    trck.set_audio_stream( audstrm )                   
    return trck

def random_album():
    albm = album.DTOAlbum()
    albm.set_album_info( gen_info.random_album_info() )
    for i in xrange( _NUM_ALBUM_TRACKS ):
        albm.add_track( random_track() )
    return albm
        
