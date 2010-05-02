import unittest

from audiobatch.model.album import AlbumInfo
from audiobatch.model._info import TimeStamp

class TestAlbumInfo( unittest.TestCase ):
    
    def test_eq( self ):
        ai = AlbumInfo( { "artists": ["Super Tramp"],
                          "composers": ["Someboyd"],
                          "title" : "Breakfast of Champions",
                          "release_date" : TimeStamp( 2007 ), } )
        ai_copy = AlbumInfo( ai )
        self.assertEquals( ai, ai_copy )

def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestAlbumInfo )

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
