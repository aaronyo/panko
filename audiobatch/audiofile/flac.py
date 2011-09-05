import logging
import mutagen.flac
from . import AudioFile

from audiobatch.model import track

_LOGGER = logging.getLogger()


# classical:
# a

_FLAC_TO_COMMON = {
    "ARTIST"      : "artists",
    "COMPOSER"    : "composers",
    "GENRE"       : "genres",
    "ISRC"        : "isrc",
    "TITLE"       : "title",
    "TRACKNUMBER" : "track_number",
    "TRACKTOTAL"  : "track_total",
    "DISCNUMBER"  : "disc_number",
    "DISCTOTAL"   : "disc_total",
    "ALBUM"       : "album.title",
    "ALBUMARTIST" : "album.artists",
    "DATE"        : "album.release_date",
    }

_COMMON_TO_FLAC = dict( (v, k) for k, v in _FLAC_TO_COMMON.iteritems() )

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

    def get_tags( self ):
        tags = track.TrackTagSet()
        flac_obj = self._flac_obj

        for flac_tag_name, value in flac_obj.items():
            flac_tag_name = flac_tag_name.upper()
            if flac_tag_name in _FLAC_TO_COMMON:
                tags.parse(_FLAC_TO_COMMON[flac_tag_name], value )
            else:                
                _LOGGER.debug( "Can't read FLAC tag "
                               + "'%s' - common mapping not found"
                               % flac_tag_name )
        return tags