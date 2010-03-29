import sys

from audiobatch.persistence import trackrepo
from audiobatch.model.track import TrackInfo
from audiobatch import console

repo = trackrepo.get_repository()

# Lookup the tracks we want to change
lib_dir = "/Volumes/fileshare/media/audio/originals"
filter = lambda track: track.get_track_info().genre == "classical"
tracks = repo.filter_tracks( lib_dir, filter )

# Interactive bits to make sure the app is doing the right thing
def prompt():
    return console.prompt( None,
                           ['y', 'n', 'l'],
                           "%d tracks to update.  Continue?" % len(tracks) )
while True:
    response = prompt()
    if response == 'l':
        for track in tracks: print track.relative_path
    else:
        break

if response != 'y':
    sys.exit( 0 )

# Change the tracks
track_info = TrackInfo()
track_info.genre = "Classical"
for track in tracks:
    repo.update_track( track, track_info = track_info )
