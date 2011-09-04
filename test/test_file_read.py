import unittest
import os.path

from audiobatch import audiofile
from audiobatch.model.time_stamp import TimeStamp

AUDIO_FILES_DIR = os.path.join( os.path.dirname(__file__), 'audio')
TRACK_1_PATH = os.path.join( AUDIO_FILES_DIR,
                             'Alex Lloyd/Black the Sun/01 Melting.flac' )
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

class TestRead( unittest.TestCase ):
    def test_read_tags__flac(self):
        trk = audiofile.read_track(TRACK_1_PATH)
        self.assertEquals(TRACK_1_TAGS, trk.tags)

    def test_read_tags__mp3(self):
        trk = audiofile.read_track(TRACK_1_PATH)
        self.assertEquals(TRACK_1_TAGS, trk.tags)
