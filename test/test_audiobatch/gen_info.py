import os
import random
import string

from audiobatch.model._info import TimeStamp
from audiobatch.model import format, track, album

_BASE_ALBUM_DICT = { "artists": ["Dire Straits"],
                       "title": "Making Movies",
                       "release_date": TimeStamp( 1980, 10, 17 ) }
_BASE_TRACK_DICT = { "artists": ["Dire Straits"],
                       "title": "Tunnel of Love",
                       "genres": ["rock", "classic rock"],
                       "track_number": 1,
                       "track_total": 8,
                       "disc_number": 1,
                       "disc_total": 1 }

_MAX_TITLE_LENGTH = 30

_TEMP_BASE_DIR = "/tmp/ab_music_dir"

def random_printable_str( max_len ):
    return ''.join( random.choice(string.printable)
                    for i in xrange( random.randint( 1, max_len ) ) )

def random_letters_str( max_len ):
    return ''.join( random.choice(string.letters)
                       for i in xrange( random.randint( 1, max_len ) ) )

def random_unicode( max_len ):
    return ''.join( unichr( random.randint(1, 0x10000) )
                    for i in xrange( random.randint( 1, max_len ) ) )

def random_temp_mp3_path():
    filename = random_letters_str( 10 ) + os.extsep + "mp3"
    return _TEMP_BASE_DIR, filename

def random_lib_name():
    return random_letters_str( 10 )

def random_album_info():
    ai = album.AlbumInfo( _BASE_ALBUM_DICT )
    ai.title = random_unicode( _MAX_TITLE_LENGTH )
    return ai

def random_track_info():
    ti = track.TrackInfo( _BASE_TRACK_DICT )
    ti.title = random_unicode( _MAX_TITLE_LENGTH )
    return ti
