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
#            os.unlink(f_path)
                
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

    def test_only_write_one_track_number(self):
        cases = [(td.TRACK_2_PATH, 'test_parts.mp3'),
                 (td.TRACK_3_PATH, 'test_parts.mp4')]
        for case in cases:
            print case
            source, target = case
            target = os.path.join(td.TEMP_DIR, target)
            shutil.copy(source, target)
            af = audiofile.load(target)
            af.tags['track_number'] = [9,10]
            af.save()
            af = audiofile.load(target)
            self.assertEquals([9], af.tags['track_number'])

    def test_read_multiple_track_number(self):
        from mutagen import id3
        from mutagen import mp4
        def package_trck(trck_list):
            return id3.TRCK( 0, ["%i/%i" % (t[0], t[1]) for t in trck_list] )
        cases = [(td.TRACK_2_PATH, 'test_parts_read.mp3', id3.ID3, 'TRCK', package_trck),
                 (td.TRACK_3_PATH, 'test_parts_read.mp4', mp4.MP4, 'trkn', lambda x: x)]
        for case in cases:
            print case
            source, target, mtg_class, mtg_key, mtg_packager = case
            target = os.path.join(td.TEMP_DIR, target)
            shutil.copy(source, target)
            mtg_file = mtg_class(target)
            mtg_file[mtg_key] = mtg_packager([[9,11],[10,11]])
            mtg_file.save()
            af = audiofile.load(target)
            self.assertEquals([9,10], af.tags['track_number'])
            
            
