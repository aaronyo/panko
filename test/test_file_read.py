import unittest
import os.path
import shutil
import datetime
import hashlib
from pprint import pprint

from audiobatch import audiofile
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

# FIXME:  NEEDED TESTS:
# * unicode
# * ...


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

class TestRead( unittest.TestCase ):
    def test_read_tags__flac(self):
        af = audiofile.load(TRACK_1_PATH)
        self.assertEquals(TRACK_1_TAGS, af.tags)

    def test_read_tags__mp3(self):
        self.maxDiff=None
        af = audiofile.load(TRACK_2_PATH)
        self.assertEquals(TRACK_2_TAGS, af.tags)
        
    def test_read_tags__mp4(self):
        af = audiofile.load(TRACK_3_PATH)
        self.assertEquals(TRACK_3_TAGS, af.tags)

    def test_read_mod_time(self):
        af = audiofile.load(TRACK_1_PATH)
        self.assertEquals( datetime.datetime(2011, 9, 18, 10, 16, 9),
                           af.mod_time )
                           
    def test_read_folder_image_path(self):
        af = audiofile.load(TRACK_1_PATH, cover_art='cover.jpg')
        self.assertTrue(af.has_folder_cover_art)
        self.assertEquals( ALBUM_1_COVER_PATH,
                           af.folder_cover_path )

    def test_read_folder_image(self):
        img = audiofile.load_folder_art(TRACK_1_PATH, filename='cover.jpg')
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
        af = audiofile.load(target)
        af.tags = TRACK_1_TAGS
        af.save()
        self.assertEquals( TRACK_1_TAGS, audiofile.load(target).tags )
        
#    def test_write__mp4(self):
#        target = os.path.join(TEMP_DIR, 'test_write.m4a')
#        shutil.copy(TRACK_3_PATH, target)
#        audiofile.write_tags(target, TRACK_1_TAGS, clear=True)
#        self.assertEquals( TRACK_1_TAGS, audiofile.read_track(target).tags )
        
    def test_image_embed_and_extract__mp3(self):
        target = os.path.join(TEMP_DIR, 'test_write_image.mp3')
        shutil.copy(TRACK_2_PATH, target)
        img = audiofile.load_folder_art(TRACK_1_PATH, "cover.jpg")
        af = audiofile.load(target)
        af.embed_cover_art(img)
        af.save()
        af = audiofile.load(target)
        self.assertTrue( af.has_embedded_cover_art )
        print(len(img.bytes), img.format)
        print(len(audiofile.load(target).extract_cover_art().bytes), audiofile.load(target).extract_cover_art().format)
        self.assertEquals( img, audiofile.load(target).extract_cover_art() )
    
#    def test_image_embed_and_extract__mp4(self):
#        target = os.path.join(TEMP_DIR, 'test_write_image.m4a')
#        shutil.copy(TRACK_3_PATH, target)
#        img = audiofile.read_folder_image(TRACK_1_PATH, "cover.jpg")
#        audiofile.embed_cover_art(target, img)
#        af = audiofile.load(target)
#        self.assertTrue( trk.has_embedded_cover_art )
#        self.assertEquals( img, audiofile.extract_cover_art(target) )
