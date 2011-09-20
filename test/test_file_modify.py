import os
import unittest
import shutil
import hashlib

from audiobatch import audiofile

from . import testdata as td

class TestWrite( unittest.TestCase ):
    def tearDown(self):
        for f in os.listdir(td.TEMP_DIR):
            f_path = os.path.join(td.TEMP_DIR, f)
            os.unlink(f_path)
                
    def test_write__mp3(self):
        target = os.path.join(td.TEMP_DIR, 'test_write.mp3')
        shutil.copy(td.TRACK_2_PATH, target)
        af = audiofile.load(target)
        af.tags = td.TRACK_1_TAGS
        af.save()
        self.assertEquals( td.TRACK_1_TAGS, audiofile.load(target).tags )
        
    def test_write__mp4(self):
        target = os.path.join(td.TEMP_DIR, 'test_write.m4a')
        shutil.copy(td.TRACK_3_PATH, target)
        af = audiofile.load(target)
        af.tags = td.TRACK_2_TAGS
        af.save()
        self.assertEquals( td.TRACK_2_TAGS, audiofile.load(target).tags )
        
    def test_image_embed_and_extract__mp3(self):
        target = os.path.join(td.TEMP_DIR, 'test_write_image.mp3')
        shutil.copy(td.TRACK_2_PATH, target)
        img = audiofile.load_folder_art(td.TRACK_1_PATH, "cover.jpg")
        af = audiofile.load(target)
        af.embed_cover(img)
        af.save()
        af = audiofile.load(target)
        self.assertTrue( af.has_embedded_cover )
        self.assertEquals( img, audiofile.load(target).extract_cover() )
    
    def test_image_embed_and_extract__mp4(self):
        target = os.path.join(td.TEMP_DIR, 'test_write_image.m4a')
        shutil.copy(td.TRACK_3_PATH, target)
        img = audiofile.load_folder_art(td.TRACK_1_PATH, "cover.jpg")
        af = audiofile.load(target)
        af.embed_cover(img)
        af.save()
        af = audiofile.load(target)
        self.assertTrue( af.has_embedded_cover )
        self.assertEquals( img, audiofile.load(target).extract_cover() )
