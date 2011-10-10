import unittest
import hashlib
import datetime
from pprint import pprint

from audiobatch import audiofile

from . import testdata as td

class TestRead( unittest.TestCase ):
    def setUp(self):
        self.maxDiff = None

    def test_read_folder_image_path(self):
        af = audiofile.open(td.FLAC_PATH)
        self.assertTrue(af.has_folder_cover())
        self.assertEquals( td.COVER_PATH,
                           af.folder_cover_path() )

    def test_read_folder_image(self):
        img = audiofile.load_folder_art(td.FLAC_PATH, filename='cover.jpg')
        self.assertEquals( open(td.COVER_PATH).read(), img.bytes )

