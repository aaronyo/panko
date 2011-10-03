import os.path
from audiobatch.model.timeutil import FlexDateTime

AUDIO_DIR = os.path.join( os.path.dirname(__file__), 'audio')
AUDIO_DIR = os.path.join( os.path.dirname(__file__), 'audio')
TEMP_DIR = os.path.join( os.path.dirname(__file__), 'temp')
TRACK_1_PATH = os.path.join( AUDIO_DIR,
                             'Alex Lloyd/Black the Sun/01 Melting.flac' )
ALBUM_1_COVER_PATH = os.path.join( AUDIO_DIR,
                                   'Alex Lloyd/Black the Sun/cover.jpg' )
TRACK_2_PATH = os.path.join( AUDIO_DIR,
                             'Dire Straits/Making Movies/01 Tunnel Of Love.mp3' )
TRACK_3_PATH = os.path.join( AUDIO_DIR,
                             'Compilations/Jazz Dance Classics Volume 1/01 Celestial Blues.m4a' )

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
    'encoder_app': ['iTunes 8.0.2'],
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
    'encoder_app': ['iTunes 8.2'],
    'encoder_params': ['vers\x00\x00\x00\x01acbf\x00\x00\x00\x03vbrq\x00\x00\x00`'],
    'is_compilation': [True],
    'album_artist': ['Various'],
    'album_title': ['Jazz Dance Classics Volume 1']
}
