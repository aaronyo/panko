""" A module for supporting persistence of 'Tracks'

This module encapsulates all details of the file system and encoding.
It is the bridge between our abstract model and persistence.
For example, searching folders and the differences between id3 tags
and vorbis comments should be contained in or below this module.

classes:
TrackRespository -- does all the work

"""

import os.path
import fnmatch
import stat
import shutil

from audiobatch.util import cache
from audiobatch.model.track import LazyTrack
from audiobatch.persistence import audiofile

_repository = None
_DEFAULT_AUDIO_EXTENSIONS= ['mp3', 'flac', 'm4a']
_DEFAULT_EXCLUDE_PATTERNS= [".*", "*/.*"]

_AudioFileData = namedtuple( "AudioFileData",
                             "base_dir, relative_path, track_info, " +
                             "album_info, container_format, stream_format, " +
                             "bitrate" )

def assemble_albums( filedata ):
    

                             

