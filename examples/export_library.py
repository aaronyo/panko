import sys

from audiobatch.service import export

lib_dir = "/Volumes/fileshare/media/audio/originals"
exp_dir = "/Volumes/fileshare/media/audio/compressed_for_portability"
def convert_test( track ):
    return (
        track.extension == "flac" # faster than checking bit rate
        or track.get_audio_stream().bitrate > 250000 )

export_job = export.prepare_export( lib_dir, exp_dir, convert_test )

print export_job.summary()
if export_job.has_work():
    print( "Continue with identified tasks?" )
    is_confirmed = raw_input( "['y' to continue] > " ) == 'y'
    if not is_confirmed:
        sys.exit( 0 )
else:
    print( "Nothing to do" )
    sys.exit( 0 )


# Use the export service's defaults for conversion and
# console output.  See audiobatch.service.export for details
# on how to use audio stream conversion tools of your choice.
export.export( export_job, "mp3" )


# TODO:
# * Fix resume on error for individual files
# * Allow long output to secondary terminal
# * Run qt.py in 3.0 compat mode
