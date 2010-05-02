import unittest
from audiobatch.model import album, track

def _dummy_track( path = "dummy" ):
    return track.Track( 0, "", path )

class TestAlbum( unittest.TestCase ):

    def test_starts_empty( self ):
        alb = album.Album()
        self.assertEquals( 0, alb.num_tracks() )

    def test_add_track( self ):
        alb = album.Album()
        alb.add_track( _dummy_track() )
        self.assertEquals( 1, alb.num_tracks() )
        self.assertEquals( _dummy_track(), alb.get_tracks()[0] )


def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestAlbum )

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
