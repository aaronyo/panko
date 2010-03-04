import mutagen.mp4
import logging


_logger = logging.getLogger();

_UNSUPPORTED = "unsupported"
_SPECIAL = "special"

_m4a2common = {
    "\xa9alb"     : "album_title",
    "aART"        : "album_artist",
    "\xa9ART"     : "artist",
    "\xa9wrt"     : "composer",
    "\xa9day"     : "date",
    _SPECIAL          : "disc_number",
    _SPECIAL          : "disc_total",
    "\xa9gen"     : "genre",
    _UNSUPPORTED   : "isrc",
    "\xa9nam"     : "title",
    _SPECIAL          : "track_number",
    _SPECIAL          : "track_total",
    }


def _cleanseForAscii( unclean ):
    if unclean.startswith( '\xa9' ):
        return r"\xa9" + unclean.replace( '\xa9' , '' )
    return unclean


def recognized( fileAbs ):
    fileObj = file(fileAbs)
    fileHeader = fileObj.read(128)
    matchScore = mutagen.mp4.MP4.score( fileAbs, fileObj, fileHeader )
    return matchScore > 0


class M4aFile():
    def __init__( self, m4aFileAbs ):
        self.m4aObj = mutagen.mp4.MP4( m4aFileAbs )

    @property
    def bitrate(self):
        return self.m4aObj.info.bitrate

    def getTags( self ):
        commonTags = {}
        
        for m4aTagName, value in self.m4aObj.items():
            firstVal = value[0]
            if m4aTagName == "disk":
                commonTags[ "disc_number" ] = firstVal[0]
                if firstVal[1] != 0:
                    commonTags[ "disc_total" ] = firstVal[1]
            elif m4aTagName == "trkn":
                commonTags[ "track_number" ] = firstVal[0]
                if firstVal[1] != 0:
                    commonTags[ "track_total" ] = firstVal[1]
            elif m4aTagName == "covr":
                # Don't want to log a warning -- just ignore this.
                # We don't refer to images as "tags"
                pass
            else:
                try:
                    commonTagName = _m4a2common[ m4aTagName ]            
                except KeyError:
                    _logger.warn("Common mapping for m4a tag '%s' not found" % _cleanseForAscii(m4aTagName))
                    continue
                unicodeValues = [unicode(x) for x in value]
                commonTags[commonTagName] = unicodeValues

        return commonTags
