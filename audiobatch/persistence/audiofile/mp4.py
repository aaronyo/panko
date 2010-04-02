import mutagen.mp4
import logging

from audiobatch.persistence.audiofile import AudioFile
from audiobatch.model import track, audiostream, format


_LOGGER = logging.getLogger()

_UNSUPPORTED = "unsupported"
_SPECIAL = "special"

_MP4_TO_COMMON = {
    "\xa9alb"     : "album.title",
    "aART"        : "album.artists",
    "\xa9ART"     : "artists",
    "\xa9wrt"     : "composers",
    "\xa9day"     : "release_date",
    _SPECIAL      : "album.disc_number",
    _SPECIAL      : "album.disc_total",
    "\xa9gen"     : "genre",
    _UNSUPPORTED  : "isrc",
    "\xa9nam"     : "title",
    _SPECIAL      : "track_number",
    _SPECIAL      : "album.track_total",
    }

EXTENSIONS = ['m4a', 'mp4']

# Logger's console output is broken for characters that do
# not have an ascii representation.  If we stop using logger for
# console output we can retire this code.  This character leads most
# mp4 tag names.
 
def _cleanse_for_ascii( unclean ):
    
    if unclean.startswith( '\xa9' ):
        return r"\xa9" + unclean.replace( '\xa9' , '', 1 )
    else:
        return unclean


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read(128)
    match_score = mutagen.mp4.MP4.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class MP4File( AudioFile ):
    def __init__( self, path ):
        self._mp4_obj = mutagen.mp4.MP4( path )
        AudioFile.__init__( self, path, self._mp4_obj )

    def get_audio_stream( self ):
        # Mutagen does not provide bitrate for ALAC nor methods for
        # differentiating ALAC and AAC (not that I could find, anyway)
        # FIXME: Needs proper bitrate implementation
        dummy_bitrate = 900000
        mp4_bitrate = self._mp4_obj.info.bitrate
        if mp4_bitrate == 0:
            return audiostream.AudioStream( dummy_bitrate,
                                            format.ALAC_STREAM,
                                            self.path )
        else:
            return audiostream.AudioStream( mp4_bitrate,
                                            audiostream.AAC_STREAM,
                                            self.path )
            


    def get_track_info( self ):
        # FIXME: How are multi vals encoded?  Have seen artists sep by '/'.
        mp4_obj = self._mp4_obj
        track_info = track.TrackInfo()
        track_info.album_info.images = self._find_folder_images()
        
        for mp4_tag_name, value in mp4_obj.items():
            if mp4_tag_name == "disk":
                first_val = value[0]
                track_info.set_tag( "album.disc_number", first_val[0] )
                if first_val[1] != 0:
                    track_info.set_tag( "album.disc_total", first_val[1] )
            elif mp4_tag_name == "trkn":
                first_val = value[0]
                track_info.set_tag( "track_number", first_val[0] )
                if first_val[1] != 0:
                    track_info.set_tag( "album.track_total", first_val[1] )
            elif mp4_tag_name == "covr":
                # FIXME: read embedded images
                pass
            else:
                try:
                    tag_name = _MP4_TO_COMMON[ mp4_tag_name ]            
                except KeyError:
                    _LOGGER.debug( "Common mapping for mp4 tag '%s' not found" \
                                       % _cleanse_for_ascii(mp4_tag_name) )
                    continue
                if not track_info.is_multi_value( tag_name ):
                    # important to call unicode() as some values are
                    # not actually strings -- only string like -- and lack
                    # important methods like the default string cmp()
                    track_info.set_tag( tag_name, unicode(value[0]) )
                else:
                    track_info.set_tag( tag_name,
                                        [ unicode(x) for x in value ] )

        return track_info