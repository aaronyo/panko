from audiobatch.model import track, audiostream
from audiobatch.persistence.audiofile import mp3, flac

lib_dir = "/Users/aaronyo/temp/lib"
exp_dir = "/Users/aaronyo/temp/exp"

real_lib_dir = "/Volumes/fileshare/media/audio/originals"

m = mp3.MP3File("/Users/aaronyo/temp/test.mp3")
print "start: ", m

t = track.TrackInfo()
t.title = u"poo"
t.artists = [u"### dude 1", u"### dude 2"]
t.album_info.artists = [u"### lady 1", u"### lady 2"]
m.extend_track_info( t )
print t
print "finish: ", m
print ""
print "########################################"
print ""
f = flac.FLACFile("/Users/aaronyo/temp/test.flac")
print "start: ", f.__dict__

t = f.get_track_info()

t.track_number = 9
t.release_date = 2006

f.extend_track_info( t )

#print "FINAL TRACK_INFO: ", t
#print "FINAL FLAC: ", f

print "FLAC STREAM: ", f.get_audio_stream().__dict__
print ""
print "########################################"
print ""


f = flac.FLACFile("/Users/aaronyo/temp/notags.flac")
s = f.get_audio_stream()

conv = audiostream.make_converter()

s2 = conv.convert(s, "mp3")

print "MP3 CONVERT: ", s2.__dict__

m = mp3.MP3File("/Users/aaronyo/temp/test.mp3")
m.set_audio_stream( s2 )
m.save()
print ""
print "######################################## IMAGES"
print ""

test_image = "/Users/aaronyo/temp/test.jpg"
from audiobatch.model import image

ai = image.makeImage( test_image )

print "dimensions from model: ", ai.get_dimensions()
print "mime type from model: ", ai.get_mime_type()
ai_resize = ai.conform_size( 500 )

print "dimensions from resized model: ", ai_resize.get_dimensions()
print "model: ", ai.__dict__
print "model resized: ", ai_resize.__dict__

f = flac.FLACFile("/Users/aaronyo/temp/notags.flac")
fims = f.get_track_info().album_info.images
print "flac's images: ", fims
print "flac's mime_type: ", fims[image.SUBJECT__ALBUM_COVER].get_mime_type()
print "flac's dimensions: ", fims[image.SUBJECT__ALBUM_COVER].get_dimensions()

m = mp3.MP3File("/Users/aaronyo/temp/test.mp3")
t = track.TrackInfo()
t.album_info.images[image.SUBJECT__ALBUM_COVER] = ai_resize
m.extend_track_info( t )
m.save()

print ""
print "######################################## LIBRARY"
print ""

from audiobatch.persistence import trackrepo
repo = trackrepo.get_repository()
all_tracks = \
    repo.all_tracks( real_lib_dir )
num_tracks = len( all_tracks )
print "num tracks: ", num_tracks

first_track = all_tracks[0]
print "first track: ", first_track.__dict__, "\n"
print "first track_info: ", first_track.get_track_info().tags(), "\n"
print "first audio_stream: ", first_track.get_audio_stream().__dict__, "\n"

import sys
import pprint
pp = pprint.PrettyPrinter(indent=4)

if len(sys.argv) > 1 and sys.argv[1] == "--slow":
    sys.stdout.flush()
    i = 0
    genres = {}
    for track in all_tracks:
        i += 1
        track_info = track.get_track_info()
        g = track_info.genre
        if g in genres:
            genres[ g ] += 1
        else:
            genres[ g ] = 1
        if i % 250 == 0:
            print "track_info_read: ", i
            sys.stdout.flush()
            
    print( "all genres: ")
    pp.pprint( genres )
    

if len(sys.argv) > 1 and sys.argv[1] == "--slow":
    print ""
    print "######################################## EXPORT"
    print ""

    from audiobatch.service import export

    job = export.prepare_export(
        lib_dir,
        exp_dir,
        convert_test = lambda track: True,
        del_matchless_targets = True)

    print job.summary()

    export.export( job, "mp3" )


    print ""
    print "######################################## FILTER"
    print ""
    
    filter = lambda track: track.get_track_info().genre == "Folk"
    repo = trackrepo.get_repository()
    tracks = repo.filter_tracks( lib_dir, filter )
    for track in tracks:
        print "filtered track: %s" % track.get_track_info().tags()
