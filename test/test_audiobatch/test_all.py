import unittest

from test_audiobatch import test_audiofile, test_track_info

all_tests = unittest.TestSuite( [ test_track_info.suite(),
                                test_audiofile.suite() ] )
unittest.TextTestRunner(verbosity=2).run( all_tests )

