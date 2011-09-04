import unittest

from audiobatch.model.track import *

class TestTrackTagSet( unittest.TestCase ):
    def test_equals_dict(self):
        dct = {'artist': 'John Doe'}
        tts = TrackTagSet(dct)
        self.assertEquals(dct, tts)