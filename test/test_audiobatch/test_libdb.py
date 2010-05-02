import copy
import unittest
from audiobatch.persistence import libdb
from test_audiobatch import gen_entity, gen_info

class TestLibDB( unittest.TestCase ):
    

    def setUp( self ):
        self._lib_name = gen_info.random_letters_str( 10 )

    def tearDown( self ):
        libdb.delete_library( self._lib_name )

    def test_save_track( self ):
        trck = gen_entity.random_track()
        libdb.save_track( self._lib_name, trck )
        reloaded_trck = libdb.load_tracks( self._lib_name )
        self.assertEquals( trck, reloaded_trck )

    def test_save_album( self ):
        albm = gen_entity.random_album()
        libdb.save_album( self._lib_name, albm )
        reloaded_albms = libdb.load_albums( self._lib_name )
        self.assertEquals( albm.get_album_info(),
                           reloaded_albms[0].get_album_info() )

    def test_save_two_albums( self ):
        albm = gen_entity.random_album()
        libdb.save_album( self._lib_name, albm )
        albm2 = gen_entity.random_album()
        libdb.save_album( self._lib_name, albm2 )
        albms = [albm, albm2]
        reloaded_albms = libdb.load_albums( self._lib_name )
        self.assertEquals( 2, len( reloaded_albms ) )
        self.assertEquals(
            [ a.get_album_info() for a in albms ].sort(),
            [ a.get_album_info() for a in reloaded_albms ].sort() )

    def test_save_album_twice( self ):
        albm = gen_entity.random_album()
        albm_copy = copy.deepcopy( albm )
        libdb.save_album( self._lib_name, albm )
        libdb.save_album( self._lib_name, albm_copy )
        reloaded_albms = libdb.load_albums( self._lib_name )
        self.assertEquals( 1, len( reloaded_albms ) )
        self.assertEquals( albm.get_album_info(),
                           reloaded_albms[0].get_album_info() )
