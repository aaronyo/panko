import unittest

from audiobatch.model.track import TrackInfo


multi_val_tags = [ "artists",
                   "composers",
                   "album.artists",
                   "album.composers",
                   "album.images" ]

single_val_tags = [ "title",
                    "track_number",
                    "track_total",
                    "disc_number",
                    "genre",
                    "release_date",
                    "isrc",
                    "album.title",
                    "album.release_date",
                    "album.isrc",
                    "album.disc_total" ]

class TestTrackInfo( unittest.TestCase ):

    def test_is_multi_val__true( self ):
        ti = TrackInfo()
        for tag_name in multi_val_tags:
            self.assertTrue( ti.is_multi_value( tag_name ),
                             "tag name '%s' should be multi val" % tag_name )
 
    def test_is_multi_val__false( self ):
        ti = TrackInfo()
        for tag_name in single_val_tags:
            self.assertFalse( ti.is_multi_value( tag_name ),
                             "tag name '%s' should not be multi val"
                             % tag_name )
 
    def test_has_tag__empty_multi_val( self ):
        ti = TrackInfo()
        for tag_name in multi_val_tags:
            self.assertFalse( ti.has_tag( tag_name ),
                              "tag '%s' should not exist" % tag_name )

    def test_has_tag__empty_single_val( self ):
        ti = TrackInfo()
        for tag_name in single_val_tags:
            self.assertFalse( ti.has_tag( tag_name ),
                              "tag '%s' should not exist" % tag_name )

    def test_tag_propogates__artists( self ):
        ti = TrackInfo()
        ti.artists = ["John Doe"]
        self.assertEquals( ti.artists, ti.get_tag("artists") )

def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestTrackInfo )

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
