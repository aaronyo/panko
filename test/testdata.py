import os.path
import shutil
from panko.audiofile.flexdatetime import FlexDateTime
from panko.audiofile.bytes import Bytes

AUDIO_DIR = os.path.join( os.path.dirname(__file__), 'data')
TEMP_DIR = os.path.join( AUDIO_DIR, 'temp')
FLAC_PATH = os.path.join( AUDIO_DIR, 'notags.flac' )
MP3_PATH = os.path.join( AUDIO_DIR, 'notags.mp3' )
M4A_PATH = os.path.join( AUDIO_DIR, 'notags.m4a' )
COVER_PATH = os.path.join( AUDIO_DIR, 'cover.jpg' )

TRACK_1_TAGS = { 
    'artist': ['Alex Lloyd'],
    'title': ['Melting'],
    'disc_number': [1],
    'track_number': [1],
    'disc_total': [1], 
    'track_total': [13],
    'isrc': ['AUEM09900036'],
    'album_artist': ['Alex Lloyd'],
    'album_title': ['Black the Sun'],
    'album_release_date': [FlexDateTime(1999, 8, 2)]
}

TRACK_2_TAGS = {
    'composer': ['Oscar Hammerstein II/Richard Rodgers/Richard Rodgers /'],
    'genre': ['Rock'],
    'title': ['Tunnel Of Love'],
    'disc_total': [1],
    'track_total': [7],
    'track_number': [1],
    'disc_number': [1],
    'artist': ['Dire Straits'],
    'album_release_date': [FlexDateTime(1980)],
    'album_title': ['Making Movies']
}

TRACK_3_TAGS = {
    'genre': ['Jazz'],
    'title': ['Celestial Blues'],
    'track_total': [8],
    'track_number': [1],
    'artist': ['Gary Bartz'],
    'is_compilation': [True],
    'album_artist': ['Various'],
    'album_title': ['Jazz Dance Classics Volume 1']
}
