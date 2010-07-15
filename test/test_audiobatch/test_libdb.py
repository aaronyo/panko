import copy
import unittest
from audiobatch.persistence import libdb
from test_audiobatch import gen_entity, gen_info

class TestLibDB( unittest.TestCase ):
    

    def setUp( self ):
        lib_name = gen_info.random_letters_str( 10 )
        self._libdb = libdb.LibDB( lib_name )

    def tearDown( self ):
        self._libdb.delete_library()

    def test_save_track( self ):
        trck = gen_entity.random_track()
        self._libdb.save_track( trck )
        reloaded_trck = self._libdb.load_tracks()
        self.assertEquals( trck, reloaded_trck )

    def test_save_album( self ):
        albm = gen_entity.random_album()
        self._libdb.save_album( albm )
        reloaded_albms = self._libdb.load_albums()
        self.assertEquals( albm.get_album_info(),
                           reloaded_albms[0].get_album_info() )

    def test_save_two_albums( self ):
        albm = gen_entity.random_album()
        self._libdb.save_album( albm )
        albm2 = gen_entity.random_album()
        self._libdb.save_album( albm2 )
        albms = [albm, albm2]
        reloaded_albms = self._libdb.load_albums()
        self.assertEquals( 2, len( reloaded_albms ) )
        self.assertEquals(
            [ a.get_album_info() for a in albms ].sort(),
            [ a.get_album_info() for a in reloaded_albms ].sort() )

    def test_save_album_twice( self ):
        albm = gen_entity.random_album()
        albm_copy = copy.deepcopy( albm )
        self._libdb.save_album( albm )
        self._libdb.save_album( albm_copy )
        reloaded_albms = self._libdb.load_albums()
        self.assertEquals( 1, len( reloaded_albms ) )
        self.assertEquals( albm.get_album_info(),
                           reloaded_albms[0].get_album_info() )

    def test_save_watch_folder( self ):
        folder = "/tmp/foo"
        self._libdb.save_watch_folder( folder )
        saved_folders = self._libdb.load_watch_folders()
        self.assertEquals( [folder], saved_folders )
