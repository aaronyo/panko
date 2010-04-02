import os.path
import shutil
import unittest

from audiobatch.persistence import audiofile
from audiobatch.model import format, track
import test_audiobatch


class TestAudioFileTags( unittest.TestCase ):

    @classmethod
    def _tempCopy( cls, path ):
        basename = os.path.basename( path )
        copy_path = os.path.join( test_audiobatch.temp_data_dir,
                                  cls.__name__ + '_' + basename )
        shutil.copyfile( path, copy_path )
        return copy_path

    def setUp( self ):
        path = test_audiobatch.notags_path( self._container_type )
        copy_path = TestAudioFileTags._tempCopy( path )
        self._audio_file = audiofile.read( copy_path )

    def tearDown( self ):
        os.unlink( self._audio_file.path )

    def test_open__no_tags( self ):
        track_info = self._audio_file.get_track_info()
        self.assertTrue( track_info.is_empty() )

    def test_save_tag__title( self ):
        self._test_save_tag( "title", "foo title" )

    def test_save_tag__genre( self ):
        self._test_save_tag( "genre", "foo genre" )

    def test_save_tag__artists( self ):
        self._test_save_tag( "artists", ["john doe", "jane doe"] )

    def test_save_tag__album_artists( self ):
        self._test_save_tag( "album.artists", ["john doe", "jane doe"] )

    def test_save_tag__track_number( self ):
        self._test_save_tag( "track_number", 1 )

    def test_save_tag__track_total( self ):
        self._test_save_tag( "track_total", 10 )

    def test_save_tag__disc_number( self ):
        self._test_save_tag( "disc_number", 2 )

    def test_save_tag__disc_number( self ):
        self._test_save_tag( "album.disc_total", 2 )

    def _test_save_tag( self, tag_name, tag_val ):
        self._test_save_tags( { tag_name : tag_val } )

    def _test_save_tags( self, tags ):
        track_info = track.TrackInfo()
        track_info.update_tags( tags )
        self._audio_file.update_track_info( track_info )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        reloaded_ti = reloaded_af.get_track_info()
        self.assertEqual( tags, reloaded_ti.tags() )

class TestMP4Tags( TestAudioFileTags ):

    def setUp( self ):
        self._container_type = format.MP4_CONTAINER
        TestAudioFileTags.setUp( self )


class TestMP3Tags( TestAudioFileTags ):

    def setUp( self ):
        self._container_type = format.MP3_CONTAINER
        TestAudioFileTags.setUp( self )


class TestFLACTags( TestAudioFileTags ):

    def setUp( self ):
        self._container_type = format.FLAC_CONTAINER
        TestAudioFileTags.setUp( self )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( TestMP4Tags )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestMP3Tags ) )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestFLACTags ) )
    return suite
