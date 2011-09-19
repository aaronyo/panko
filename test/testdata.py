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
    'artists': ['Alex Lloyd'],
    'titles': ['Melting'],
    'disc_number': 1,
    'track_number': 1,
    'disc_total': 1, 
    'track_total': 13,
    'isrc': 'AUEM09900036',
    'album_artists': ['Alex Lloyd'],
    'album_titles': ['Black the Sun'],
    'album_release_date': FlexDateTime(1999, 8, 2)
}

TRACK_2_TAGS = {
    'composers': ['Oscar Hammerstein II/Richard Rodgers/Richard Rodgers /'],
    'genres': ['Rock'],
    'titles': ['Tunnel Of Love'],
    'disc_total': 1,
    'track_total': 7,
    'track_number': 1,
    'disc_number': 1,
    'encoding_tool': 'iTunes 8.0.2',
    'artists': ['Dire Straits'],
    'album_release_date': FlexDateTime(1980),
    'album_titles': ['Making Movies']
}

TRACK_3_TAGS = {
    'genres': ['Jazz'],
    'titles': ['Celestial Blues'],
    'track_total': 8,
    'track_number': 1,
    'artists': ['Gary Bartz'],
    'encoding_tool': 'iTunes 8.2',
    'is_compilation': True,
    'album_artists': ['Various'],
    'album_titles': ['Jazz Dance Classics Volume 1']
}
