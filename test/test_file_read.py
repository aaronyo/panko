import unittest
import hashlib
import datetime
from pprint import pprint

from audiobatch import audiofile

from . import testdata as td

class TestRead( unittest.TestCase ):
    def test_read_tags__flac(self):
        af = audiofile.load(td.TRACK_1_PATH)
        self.assertEquals(td.TRACK_1_TAGS, af.tags)

    def test_read_tags__mp3(self):
        self.maxDiff=None
        af = audiofile.load(td.TRACK_2_PATH)
        self.assertEquals(td.TRACK_2_TAGS, af.tags)
        
    def test_read_tags__mp4(self):
        af = audiofile.load(td.TRACK_3_PATH)
        self.assertEquals(td.TRACK_3_TAGS, af.tags)

    def test_read_mod_time(self):
        af = audiofile.load(td.TRACK_1_PATH)
        self.assertEquals( datetime.datetime(2011, 9, 18, 10, 16, 9),
                           af.mod_time )
                           
    def test_read_folder_image_path(self):
        af = audiofile.load(td.TRACK_1_PATH, cover_art='cover.jpg')
        self.assertTrue(af.has_folder_cover)
        self.assertEquals( td.ALBUM_1_COVER_PATH,
                           af.folder_cover_path )

    def test_read_folder_image(self):
        img = audiofile.load_folder_art(td.TRACK_1_PATH, filename='cover.jpg')
        self.assertEquals( open(td.ALBUM_1_COVER_PATH).read(), img.bytes )

