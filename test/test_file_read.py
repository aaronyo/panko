import unittest
import os.path
import shutil
import datetime
import hashlib
from pprint import pprint

from audiobatch import audiofile
from audiobatch import trackimage
from audiobatch.model.timeutil import LenientDate
from audiobatch.model.track import TrackTagSet

AUDIO_DIR = os.path.join( os.path.dirname(__file__), 'audio')
AUDIO_DIR = os.path.join( os.path.dirname(__file__), 'audio')
TEMP_DIR = os.path.join( os.path.dirname(__file__), 'temp')
TRACK_1_PATH = os.path.join( AUDIO_DIR,
                             'Alex Lloyd/Black the Sun/01 Melting.flac' )
ALBUM_1_COVER_PATH = os.path.join( AUDIO_DIR,
                                   'Alex Lloyd/Black the Sun/cover.jpg' )
TRACK_2_PATH = os.path.join( AUDIO_DIR,
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
        'release_date': LenientDate.parse( '1999-08-02' )
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
        'release_date': LenientDate.parse('1980'),
        'title': 'Making Movies'
    }
}

class TestRead( unittest.TestCase ):
    def test_read_tags__flac(self):
        trk = audiofile.read_track(TRACK_1_PATH)
        pprint(trk.tags)
        self.assertEquals(TRACK_1_TAGS, trk.tags)

    def test_read_tags__mp3(self):
        trk = audiofile.read_track(TRACK_2_PATH)
        pprint(trk.tags)
        self.assertEquals(TRACK_2_TAGS, trk.tags)
        
    def test_read_mod_time(self):
        trk = audiofile.read_track(TRACK_1_PATH)
        self.assertEquals( datetime.datetime(2011, 8, 28, 11, 1, 39),
                           trk.mod_time )
                           
    def test_read_folder_image_path(self):
        trk = audiofile.read_track(TRACK_1_PATH, cover='cover.jpg')
        self.assertEquals(ALBUM_1_COVER_PATH, trk.cover.path)

    def test_folder_image_has_bytes(self):
        trk = audiofile.read_track(TRACK_1_PATH, cover='cover.jpg')
        img = trackimage.read_image(trk.cover)
        expected = hashlib.md5(open(ALBUM_1_COVER_PATH).read()).hexdigest()
        # compare hashes to keep failure messages short
        self.assertEquals( expected, hashlib.md5(img.bytes).hexdigest() )

class TestWrite( unittest.TestCase ):
    def tearDown(self):
        for f in os.listdir(TEMP_DIR):
            f_path = os.path.join(TEMP_DIR, f)
            os.unlink(f_path)
                
    def test_write__mp3(self):
        target = os.path.join(TEMP_DIR, 'test_write.mp3')
        shutil.copy(TRACK_2_PATH, target)
        audiofile.write_tags(target, TRACK_1_TAGS, clear=True)
        self.assertEquals( TRACK_1_TAGS, audiofile.read_track(target).tags )