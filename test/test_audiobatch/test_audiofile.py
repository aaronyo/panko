import unittest

from audiobatch.persistence import audiofile
from audiobatch.model import format
import test_audiobatch


class TestAudioFileTags( unittest.TestCase ):

    def setUp( self ):
        pass

    def tearDown( self ):
        pass

    def test_open__no_tags( self ):
        path = test_audiobatch.notags_path( self._container_type )
        audio_file = audiofile.read( path )
        track_info = audio_file.get_track_info()
        print track_info.tags()
        self.assertTrue( track_info.is_empty() )


class TestMP4Tags( TestAudioFileTags ):

    def setUp( self ):
        self._container_type = format.MP4_CONTAINER
        TestAudioFileTags.setUp( self )


def suite():
    return unittest.TestLoader().loadTestsFromTestCase( TestMP4Tags )
