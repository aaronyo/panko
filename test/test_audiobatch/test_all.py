import unittest

import audiobatch.console
from test_audiobatch import test_audiofile, test_track_info, test_album
from test_audiobatch import test_album_info, test_info

audiobatch.console._setup_console_logging()
all_tests = unittest.TestSuite( [ test_track_info.suite(),
                                  test_audiofile.suite(),
                                  test_album.suite(),
                                  test_album_info.suite(),
                                  test_info.suite() ] )
unittest.TextTestRunner(verbosity=2).run( all_tests )

