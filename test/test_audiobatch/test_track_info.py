import unittest

from audiobatch.model.track import TrackInfo


multi_val_tags = [ "artists",
                   "composers",
                   "album.artists",
                   "album.composers",
                   "album.images" ]

single_val_tags = [ "title",
                    "track_number",
                    "genre",
                    "release_date",
                    "isrc",
                    "album.title",
                    "album.release_date",
                    "album.isrc",
                    "album.track_total",
                    "album.disc_number",
                    "album.disc_total" ]

class TestTrackInfo( unittest.TestCase ):

    def test_is_multi_val__true( self ):
        track = TrackInfo()
        for tag_name in multi_val_tags:
            self.assertTrue( track.is_multi_value( tag_name ),
                             "tag name '%s' should be multi val" % tag_name )
 
    def test_is_multi_val__false( self ):
        track = TrackInfo()
        for tag_name in single_val_tags:
            self.assertFalse( track.is_multi_value( tag_name ),
                             "tag name '%s' should not be multi val"
                             % tag_name )
 
    def test_has_tag__empty_multi_val( self ):
        track = TrackInfo()
        for tag_name in multi_val_tags:
            self.assertFalse( track.has_tag( tag_name ),
                              "tag '%s' should not exist" % tag_name )

    def test_has_tag__empty_single_val( self ):
        track = TrackInfo()
        for tag_name in single_val_tags:
            self.assertFalse( track.has_tag( tag_name ),
                              "tag '%s' should not exist" % tag_name )

def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestTrackInfo )
                             
