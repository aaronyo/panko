import unittest
from audiobatch.model._info import TimeStamp

_stamp = [1999, 12, 31, 11, 59, 59]
_stamp_str = "1999-12-31 11:59:59"

class TestTimeStamp( unittest.TestCase ):
    
    def test_construct__year( self ):
        s = TimeStamp( *_stamp[:1] )
        self.assertEqual( _stamp[0], s.year )
        
    def test_construct__month( self ):
        s = TimeStamp( *_stamp[:2] )
        self.assertEqual( _stamp[1], s.month )

    def test_construct__day( self ):
        s = TimeStamp( *_stamp[:3] )
        self.assertEqual( _stamp[2], s.day )

    def test_construct__hour( self ):
        s = TimeStamp( *_stamp[:4] )
        self.assertEqual( _stamp[3], s.hour )

    def test_construct__min( self ):
        s = TimeStamp( *_stamp[:5] )
        self.assertEqual( _stamp[4], s.min )

    def test_construct__sec( self ):
        s = TimeStamp( *_stamp[:6] )
        self.assertEqual( _stamp[5], s.sec )

    def test_construct__all_fields( self ):
        s = TimeStamp( *_stamp[:6] )
        self.assertEqual( _stamp[0], s.year )
        self.assertEqual( _stamp[1], s.month )
        self.assertEqual( _stamp[2], s.day )
        self.assertEqual( _stamp[3], s.hour )
        self.assertEqual( _stamp[4], s.min )
        self.assertEqual( _stamp[5], s.sec )

    def test_str__year( self ):
        s = TimeStamp( *_stamp[:1] )
        self.assertEqual( _stamp_str[:4], str( s ) )

    def test_str__month( self ):
        s = TimeStamp( *_stamp[:2] )
        self.assertEqual( _stamp_str[:7], str( s ) )

    def test_str__day( self ):
        s = TimeStamp( *_stamp[:3] )
        self.assertEqual( _stamp_str[:10], str( s ) )

    def test_str__hour( self ):
        s = TimeStamp( *_stamp[:4] )
        self.assertEqual( _stamp_str[:13], str( s ) )

    def test_str__min( self ):
        s = TimeStamp( *_stamp[:5] )
        self.assertEqual( _stamp_str[:16], str( s ) )

    def test_str__sec( self ):
        s = TimeStamp( *_stamp[:6] )
        self.assertEqual( _stamp_str, str( s ) )

    def test_invalid__low_year( self ):
        self.assertRaises( ValueError, TimeStamp, 0 )
        
    def test_invalid__high_year( self ):
        self.assertRaises( ValueError, TimeStamp, 10000 )

    def test_invalid__low_month( self ):
        bad_s = list(_stamp)
        bad_s[1] = 0
        self.assertRaises( ValueError, TimeStamp, bad_s )
        
    def test_invalid__high_month( self ):
        bad_s = list(_stamp)
        bad_s[1] = 13
        self.assertRaises( ValueError, TimeStamp, bad_s )

    def test_invalid__high_day( self ):
        bad_s = list(_stamp)
        bad_s[1] = 11 # November doesn't have 31 days
        self.assertRaises( ValueError, TimeStamp, bad_s )

    def test_invalid__low_day( self ):
        bad_s = list(_stamp)
        bad_s[2] = 0
        self.assertRaises( ValueError, TimeStamp, bad_s )

    def test_invalid__low_hour( self ):
        bad_s = list(_stamp)
        bad_s[3] = -1
        self.assertRaises( ValueError, TimeStamp, bad_s )
        
    def test_invalid__high_hour( self ):
        bad_s = list(_stamp)
        bad_s[3] = 24
        self.assertRaises( ValueError, TimeStamp, bad_s )

    def test_invalid__low_min( self ):
        bad_s = list(_stamp)
        bad_s[4] = -1
        self.assertRaises( ValueError, TimeStamp, bad_s )
        
    def test_invalid__high_min( self ):
        bad_s = list(_stamp)
        bad_s[4] = 60
        self.assertRaises( ValueError, TimeStamp, bad_s )

    def test_invalid__low_sec( self ):
        bad_s = list(_stamp)
        bad_s[5] = -1
        self.assertRaises( ValueError, TimeStamp, bad_s )
        
    def test_invalid__high_sec( self ):
        bad_s = list(_stamp)
        bad_s[5] = 60
        self.assertRaises( ValueError, TimeStamp, bad_s )

def suite():
    suite = unittest.TestLoader().loadTestsFromTestCase( TestTimeStamp )
    return suite

if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run( suite() )
