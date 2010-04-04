import os.path
import shutil
import unittest

from audiobatch.persistence import audiofile
from audiobatch.model import format, track
import test_audiobatch


class TestAudioFileFields( unittest.TestCase ):

    @classmethod
    def _tempCopy( cls, path ):
        basename = os.path.basename( path )
        copy_path = os.path.join( test_audiobatch.temp_data_dir,
                                  cls.__name__ + '_' + basename )
        shutil.copyfile( path, copy_path )
        return copy_path

    def setUp( self ):
        path = test_audiobatch.notags_path( self._container_type )
        copy_path = TestAudioFileFields._tempCopy( path )
        self._audio_file = audiofile.read( copy_path )

    def tearDown( self ):
        os.unlink( self._audio_file.path )

    def test_open__no_fields( self ):
        track_info = self._audio_file.get_track_info()
        self.assertTrue( len( track_info ) == 0 )

    def test_save_field__title( self ):
        self._test_save_field( "title", "foo title" )

    def test_save_field__genre( self ):
        self._test_save_field( "genre", "foo genre" )

    def test_save_field__artists( self ):
        self._test_save_field( "artists", ["john doe", "jane doe"] )

    def test_save_field__album_artists( self ):
        self._test_save_field( "album.artists", ["john doe", "jane doe"] )

    def test_save_field__track_number( self ):
        self._test_save_field( "track_number", 1 )

    def test_save_field__track_total( self ):
        self._test_save_field( "track_total", 10 )

    def test_save_field__disc_number( self ):
        self._test_save_field( "disc_number", 2 )

    def test_save_field__disc_number( self ):
        self._test_save_field( "album.disc_total", 2 )

    def test_save_fields__track_pos( self ):
        self._test_save_fields( { "track_number": 5, "track_total": 12 } )

    def test_save_fields__disc_pos( self ):
        self._test_save_fields( { "disc_number": 2, "album.disc_total": 2 } )

    def _test_save_field( self, field_name, field_val ):
        self._test_save_fields( { field_name : field_val } )

    def _test_save_fields( self, fields ):
        track_info = track.TrackInfo()
        track_info.update( fields )
        self._audio_file.update_track_info( track_info )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        reloaded_ti = reloaded_af.get_track_info()
        self.assertEqual( fields.items(), reloaded_ti.items() )

class TestMP4Fields( TestAudioFileFields ):

    def setUp( self ):
        self._container_type = format.MP4_CONTAINER
        TestAudioFileFields.setUp( self )


class TestMP3Fields( TestAudioFileFields ):

    def setUp( self ):
        self._container_type = format.MP3_CONTAINER
        TestAudioFileFields.setUp( self )


class TestFLACFields( TestAudioFileFields ):

    def setUp( self ):
        self._container_type = format.FLAC_CONTAINER
        TestAudioFileFields.setUp( self )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( TestMP4Fields )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestMP3Fields ) )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestFLACFields ) )
    return suite
