import unittest
import os.path

from audiobatch import audiofile
from audiobatch.model.time_stamp import TimeStamp

AUDIO_FILES_DIR = os.path.join( os.path.dirname(__file__), 'audio')
TRACK_1_PATH = os.path.join( AUDIO_FILES_DIR,
                             'Alex Lloyd/Black the Sun/01 Melting.flac' )
TRACK_2_PATH = os.path.join( AUDIO_FILES_DIR,
                             'Dire Straits/Making Movies/01 Tunnel Of Love.mp3' )

TRACK_1_TAGS = { 
    'artists': ['Alex Lloyd'],
    'title': 'Melting',
    'disc_number': 1,
    'track_number': 1,
    'disc_total': 1, 
    'track_total': 13,
    'isrc': 'AUEM09900036',
    'album': { 
        'artists': ['Alex Lloyd'],
        'title': 'Black the Sun',
        'release_date': TimeStamp.parse( '1999-08-02' )
    }
}

TRACK_2_TAGS = {
    'composers': ['Oscar Hammerstein II/Richard Rodgers/Richard Rodgers /'],
    'genres': ['Rock'],
    'title': 'Tunnel Of Love',
    'disc_total': 1,
    'track_total': 7,
    'track_number': 1,
    'disc_number': 1,
    'artists': ['Dire Straits'],
    'album': {
        'release_date': TimeStamp.parse('1980'),
        'title': 'Making Movies'
    }
}

class TestRead( unittest.TestCase ):
    def test_read_tags__flac(self):
        trk = audiofile.read_track(TRACK_1_PATH)
        self.assertEquals(TRACK_1_TAGS, trk.tags)

    def test_read_tags__mp3(self):
        trk = audiofile.read_track(TRACK_2_PATH)
        print trk.raw_tags
        
        self.assertEquals(TRACK_2_TAGS, trk.tags)
