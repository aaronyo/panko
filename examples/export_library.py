"""
An example for exporting a high quality audio library to compressed format.

I use this script to export my mixed format "originals," which include
FLAC, ALAC, M4P and MP3, to compressed mp3 files.  Files that already
meet the bitrate requirement (see 'convert_test') are considered compressed
already and are simply copied to the export folder to prevent unnecessary
quality loss.

Subsequent runs perform differential updates and remove previously exported
audio whose original has been deleted.

The relative paths of the exported files will match the relative paths of the
original files (minus extension, of course).
"""

import sys
from optparse import OptionParser

from audiobatch.service import export
from audiobatch import console

lib_dir = "/Volumes/fileshare/media/audio/originals"
exp_dir = "/Volumes/fileshare/media/audio/compressed_for_portability"
def convert_test( track ):
    return (
        track.extension == "flac" # faster than checking bit rate
        or track.get_audio_stream().bitrate > 250000 )

export_job = export.prepare_export( lib_dir,
                                    exp_dir,
                                    convert_test,
                                    del_matchless_targets = True)

print export_job.summary()
print ""
if export_job.has_work():
    response = console.prompt( None,
                               ["y", "n"],
                               "Continue with identified tasks?" )
    if not response.lower() == 'y':
        sys.exit( 0 )
else:
    print( "Nothing to do" )
    sys.exit( 0 )


# Use the export service's defaults for conversion and for
# console output.  See audiobatch.service.export for details
# on how to use audio stream conversion tools of your choice.
export.export( export_job, "mp3" )
