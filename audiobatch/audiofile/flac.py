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

    def get_raw_tags( self ):
        return dict(self._flac_obj)
        
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
            
    def update_tags( self, tags ):
        flat_tags = tags.flat()
        for field_name, value in flat_tags.items():
            # Mutagen FLAC dictionary access coverts
            # single elements to lists (since all vorbis comments are
            # lists).  Since it handles this conversion for us, we don't need
            # the same special handling as we did when reading the track_info
            if field_name in _COMMON_TO_FLAC:
                self._flac_obj[ _COMMON_TO_FLAC[ field_name ] ]= \
                    AudioFile._unicode_all( value )
            else:
                _LOGGER.error( "Can't write '%s' - FLAC mapping not found"
                               % field_name )
                
    def save( self ):
        self._flac_obj.save()
