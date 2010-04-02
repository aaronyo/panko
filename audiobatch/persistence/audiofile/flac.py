import logging
import mutagen.flac
from audiobatch.persistence.audiofile import AudioFile

from audiobatch.model import track, audiostream, format

_LOGGER = logging.getLogger()

_FLAC_TO_COMMON = {
    "ARTIST"      : "artists",
#   FIXME: "PERFORMER"   : ,
    "DATE"        : "release_date",
    "GENRE"       : "genre",
    "ISRC"        : "isrc",
    "TITLE"       : "title",
    "TRACKNUMBER" : "track_number",
    "TRACKTOTAL"  : "album.track_total",
    "ALBUM"       : "album.title",
    "ALBUMARTIST" : "album.artists",
    "DISCNUMBER"  : "album.disc_number",
    "DISCTOTAL"   : "album.disc_total",
    }

_COMMON_TO_FLAC = dict( (value, key) 
                        for key, value 
                        in _FLAC_TO_COMMON.iteritems()
                        )


EXTENSIONS = ['flac']

def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read(128)
    match_score = mutagen.flac.FLAC.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class FLACFile( AudioFile ):
    def __init__( self, path ):
        self._flac_obj = mutagen.flac.FLAC( path )
        AudioFile.__init__( self, path, self._flac_obj )
        
    def get_audio_stream( self ):
        # Mutagen does not provide bitrate for FLAC
        # FIXME: Provide proper bitrate implementation
        dummy_bitrate = 900000
        return audiostream.AudioStream( dummy_bitrate,
                                        format.FLAC_STREAM,
                                        self.path )

    def get_track_info( self ):
        track_info = track.TrackInfo()
        track_info.album_info.images = self._find_folder_images()

        for tag_name, flac_tag_name in _COMMON_TO_FLAC.items():
            if flac_tag_name in self._flac_obj:
                val = self._flac_obj[ flac_tag_name ]
                # FLAC models all attributes as a list but TrackInfo does not
                if not track_info.is_multi_value( tag_name ):
                    track_info.set_tag( tag_name, val[0] )
                else:
                    track_info.set_tag( tag_name, val )

        #FIXME: read embedded images

        return track_info
            
    def extend_track_info( self, track_info ):
        for tag_name, flac_tag_name in _COMMON_TO_FLAC.items():
            # Mutagen FLAC dictionary access is not symmetric.  It coverts
            # single elements to lists (since all vorbis comments are
            # lists).  Since it handles this conversion for us, we don't need
            # the same special handling as we did when reading the track_info
            #
            if track_info.has_tag( tag_name ):
                self._flac_obj[ flac_tag_name ] = \
                    track_info.get_tag_unicode( tag_name )

    def save( self ):
        self._flac_obj.save()
