import mutagen.mp4
import logging


_LOGGER = logging.getLogger()

_UNSUPPORTED = "unsupported"
_SPECIAL = "special"

_M4A_TO_COMMON = {
    "\xa9alb"     : "album_title",
    "aART"        : "album_artist",
    "\xa9ART"     : "artist",
    "\xa9wrt"     : "composer",
    "\xa9day"     : "date",
    _SPECIAL      : "disc_number",
    _SPECIAL      : "disc_total",
    "\xa9gen"     : "genre",
    _UNSUPPORTED  : "isrc",
    "\xa9nam"     : "title",
    _SPECIAL      : "track_number",
    _SPECIAL      : "track_total",
    }


# Logger's console output is broken for characters that do
# not have an ascii representation.  If we stop using logger for
# console output we can retire this code.  This character leads most
# m4a tag names.
 
def _cleanse_for_ascii( unclean ):
    if unclean.startswith( '\xa9' ):
        return r"\xa9" + unclean.replace( '\xa9' , '' )
    return unclean


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read(128)
    match_score = mutagen.mp4.MP4.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class M4aFile():
    def __init__( self, path ):
        self.m4a_obj = mutagen.mp4.MP4( path )

    @property
    def bitrate(self):
        return self.m4a_obj.info.bitrate

    def get_tags( self ):
        common_tags = {}
        
        for m4a_tag_name, value in self.m4a_obj.items():
            first_val = value[0]
            if m4a_tag_name == "disk":
                common_tags[ "disc_number" ] = first_val[0]
                if first_val[1] != 0:
                    common_tags[ "disc_total" ] = first_val[1]
            elif m4a_tag_name == "trkn":
                common_tags[ "track_number" ] = first_val[0]
                if first_val[1] != 0:
                    common_tags[ "track_total" ] = first_val[1]
            elif m4a_tag_name == "covr":
                # Don't want to log a warning -- just ignore this.
                # We don't refer to images as "tags"
                pass
            else:
                try:
                    common_tag_name = _M4A_TO_COMMON[ m4a_tag_name ]            
                except KeyError:
                    _LOGGER.warn( "Common mapping for m4a tag '%s' not found" \
                                     % _cleanse_for_ascii(m4a_tag_name) )
                    continue
                unicode_values = [unicode(x) for x in value]
                common_tags[common_tag_name] = unicode_values

        return common_tags
