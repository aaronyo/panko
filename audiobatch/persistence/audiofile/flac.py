import logging
import mutagen.flac
from audiobatch.persistence.audiofile import AudioFile

from audiobatch.model import track, album, audiostream, format

_LOGGER = logging.getLogger()


# classical:
# a

_FLAC_TO_COMMON = {
    "ARTIST"      : "artists",
#   FIXME: "PERFORMER"   : ,
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

    def _get_info( self ):

        def _update_field( info, field_name, flac_value ):
            if info.is_multi_value( field_name ):
                info[field_name] = flac_value
            else:
                first_val = flac_value[0]
                if info.is_int( field_name ):
                    first_val = int( first_val )
                info[field_name] = first_val

        album_info = album.AlbumInfo()
        track_info = track.TrackInfo()

        flac_obj = self._flac_obj

        for flac_tag_name, value in flac_obj.items():
            flac_tag_name = flac_tag_name.upper()
            if flac_tag_name in _FLAC_TO_COMMON:
                field_name = _FLAC_TO_COMMON[ flac_tag_name ]
                val = flac_obj[ flac_tag_name ]
                if field_name.startswith("album."):
                    field_name = field_name[6:]
                    _update_field( album_info, field_name, val )
                else:
                    _update_field( track_info, field_name, val )
            else:                
                _LOGGER.debug( "Can't read FLAC tag "
                               + "'%s' - common mapping not found"
                               % flac_tag_name )

        return album_info, track_info

            
    def _update_track_info( self, track_info ):
        for field_name, value in track_info.items():
            # Mutagen FLAC dictionary access coverts
            # single elements to lists (since all vorbis comments are
            # lists).  Since it handles this conversion for us, we don't need
            # the same special handling as we did when reading the track_info
            if field_name == "images":
                #FIXME: handle saving embedded images in FLAC
                continue
            if field_name in _COMMON_TO_FLAC:
                self._flac_obj[ _COMMON_TO_FLAC[ field_name ] ]= \
                    AudioFile._unicode_all( track_info[ field_name ] )
            else:
                _LOGGER.error( "Can't write '%s' - FLAC mapping not found"
                               % field_name )
                
    def _update_album_info( self, album_info ):
        for field_name, value in album_info.items():
            lookup_name = "album." + field_name
            if lookup_name in _COMMON_TO_FLAC:
                self._flac_obj[ _COMMON_TO_FLAC[ lookup_name ] ]= \
                    AudioFile._unicode_all( album_info[ field_name ] )
            else:
                _LOGGER.error( "Can't write '%s' - FLAC mapping not found"
                               % lookup_name )

    def save( self ):
        self._flac_obj.save()
