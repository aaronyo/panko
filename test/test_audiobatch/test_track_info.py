import unittest

from audiobatch.model.track import TrackInfo


multi_val_tags = [ "artists",
                   "genres",
                   "composers" ]

single_val_tags = [ "title",
                    "track_number",
                    "track_total",
                    "disc_number",
                    "disc_total",
                    "isrc" ]

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
            self.assertFalse( tag_name in ti,
                              "tag '%s' should not exist" % tag_name )

    def test_has_tag__empty_single_val( self ):
        ti = TrackInfo()
        for tag_name in single_val_tags:
            self.assertFalse( tag_name in ti,
                              "tag '%s' should not exist" % tag_name )

    def test_field_propogates__artists( self ):
        ti = TrackInfo()
        ti.artists = ["John Doe"]
        self.assertEquals( ["John Doe"], ti["artists"] )
        self.assertTrue( "artists" in ti )
        self.assertEquals( ti.artists, ti["artists"] )

    def test_dict_propogates__artists( self ):
        ti = TrackInfo()
        ti["artists"] = ["John Doe"]
        self.assertEquals( ["John Doe"], ti.artists )
        self.assertTrue( "artists" in ti )
        self.assertEquals( ti["artists"], ti.artists )

    def test_construct__multiple_fields( self ):
        ti = TrackInfo( { "artists": ["Big Bird"],
                          "genres": ["Childrens", "Rock"] } )
        self.assertEquals( ["Big Bird"], ti.artists )
        self.assertEquals( ["Childrens", "Rock"], ti.genres )

    def test_dict_eq__symmetric( self ):
        d = { "artists": ["Big Bird"],
              "genres": ["Childrens", "Rock"] }
        ti = TrackInfo( d )
        self.assertEquals( ti, d )
        self.assertEquals( d, ti )

    def test_dict_eq__order_doesnt_matter( self ):
        d = { "artists": ["Big Bird"],
              "genres": ["Childrens", "Rock"] }
        d2 = { "genres": ["Childrens", "Rock"],
               "artists": ["Big Bird"] }
        ti = TrackInfo( d2 )
        self.assertEquals( ti, d )
        self.assertEquals( d, ti )

def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestTrackInfo )

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
