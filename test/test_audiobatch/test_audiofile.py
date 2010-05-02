import os.path
import shutil
import unittest

from audiobatch.persistence import audiofile
from audiobatch.model import format, track, album
from audiobatch.model._info import TimeStamp
import test_audiobatch
from test_audiobatch import gen_info

class BaseTestAudioFileFields():

    @classmethod
    def _tempCopy( cls, path ):
        basename = os.path.basename( path )
        copy_path = os.path.join( test_audiobatch.temp_data_dir,
                                  cls.__name__ + '_' + basename )
        shutil.copyfile( path, copy_path )
        return copy_path

    def setUp( self ):
        path = test_audiobatch.notags_path( self._container_type )
        copy_path = BaseTestAudioFileFields._tempCopy( path )
        self._audio_file = audiofile.read( copy_path )

    def tearDown( self ):
        os.unlink( self._audio_file.path )

    def test_open__no_fields( self ):
        album_info, track_info = self._audio_file.get_info()
        self.assertTrue( len( track_info ) == 0 )
        self.assertTrue( len( album_info ) == 0 )

    def test_roundtrip__title( self ):
        self._test_roundtrip_track_fields( { "title": "foo title" } )

    def test_roundtrip__genre( self ):
        self._test_roundtrip_track_fields( { "genres": ["foo genre"] } )

    def test_roundtrip__artists( self ):
        self._test_roundtrip_track_fields( 
            { "artists": ["john doe", "jane doe"] } )

    def test_roundtrip__album_artists( self ):
        self._test_roundtrip_album_fields(
            { "artists": ["john doe", "jane doe"] } )

    def test_roundtrip__composers( self ):
        self._test_roundtrip_track_fields( { "composers": ["Mark Knopfler"] } )

    def test_roundtrip__isrc( self ):
        self._test_roundtrip_track_fields( { "isrc": "ABCD123456789" } )

    def test_roundtrip__album_release_date( self ):
        self._test_roundtrip_album_fields(
            { "release_date": TimeStamp( 2000, 1, 1) } )

    def test_roundtrip__track_number( self ):
        self._test_roundtrip_track_fields( { "track_number": 1 } )

    def test_roundtrip__track_total( self ):
        self._test_roundtrip_track_fields( { "track_total": 12 } )

    def test_roundtrip__disc_number( self ):
        self._test_roundtrip_track_fields( { "disc_number": 2 } )

    def test_roundtrip__disc_total( self ):
        self._test_roundtrip_track_fields( { "disc_total": 2 } )

    def test_roundtrip__all_position_fields( self ):
        self._test_roundtrip_track_fields(
            { "track_number": 5,
              "track_total": 17,
              "disc_number": 1,
              "disc_total": 2 } )

    def test_roundtrip__all_working_fields( self ):
        self._test_roundtrip_fields(
            album_dict = gen_info.random_album_info(),
            track_dict = gen_info.random_track_info() )

    def _test_roundtrip_track_fields( self, fields_dict ):
        self._audio_file.update_info( track.TrackInfo( fields_dict ) )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        _, reloaded_ti = reloaded_af.get_info()
        self.assertEqual( fields_dict, reloaded_ti )

    def _test_roundtrip_album_fields( self, fields_dict, infidelity_dict = {} ):
        self._audio_file.update_info( album.AlbumInfo( fields_dict ) )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        reloaded_ai, _ = reloaded_af.get_info()
        expected_dict = dict( fields_dict )
        expected_dict.update( infidelity_dict )
        self.assertEqual( expected_dict, reloaded_ai )

    def _test_roundtrip_fields( self,
                                album_dict,
                                track_dict,
                                album_infidelity_dict = {} ):
        self._audio_file.update_info( album.AlbumInfo( album_dict ) )
        self._audio_file.update_info( track.TrackInfo( track_dict ) )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        reloaded_ai, reloaded_ti = reloaded_af.get_info()
        self.assertEqual( track_dict, dict( reloaded_ti ) )

        expected_dict = dict( album_dict )
        expected_dict.update( album_infidelity_dict )
        self.assertEqual( expected_dict, dict( reloaded_ai ) )


class TestMP4Fields( BaseTestAudioFileFields, unittest.TestCase ):

    def setUp( self ):
        self._container_type = format.MP4_CONTAINER
        BaseTestAudioFileFields.setUp( self )

    def test_roundtrip__album_release_date( self ):
        ''' Only the year is persisted for MP4 a la iTunes'''
        self._test_roundtrip_album_fields(
            { "release_date": TimeStamp( 2000, 1, 1) },
            infidelity_dict = { "release_date": TimeStamp( 2000 ) } )

    def test_roundtrip__all_working_fields( self ):
        album_info = gen_info.random_album_info()
        year_only = TimeStamp( album_info.release_date.year )
        self._test_roundtrip_fields(
            album_dict = album_info,
            track_dict = gen_info.random_track_info(),
            album_infidelity_dict = \
                { "release_date": year_only } )

    def test_roundtrip__isrc( self ):
        ''' isrc is not persisted at all for MP4'''
        track_info = track.TrackInfo( { "isrc": "ABCD123456789" } )
        self._audio_file.update_info( track_info )
        self._audio_file.save()
        reloaded_af = audiofile.read( self._audio_file.path )
        _, reloaded_ti = reloaded_af.get_info()
        self.assertEqual( 0, len( reloaded_ti ) )

class TestMP3Fields( BaseTestAudioFileFields, unittest.TestCase ):

    def setUp( self ):
        self._container_type = format.MP3_CONTAINER
        BaseTestAudioFileFields.setUp( self )


class TestFLACFields( BaseTestAudioFileFields, unittest.TestCase ):

    def setUp( self ):
        self._container_type = format.FLAC_CONTAINER
        BaseTestAudioFileFields.setUp( self )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( TestFLACFields )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestMP3Fields ) )
    suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase( TestMP4Fields ) )

    return suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
