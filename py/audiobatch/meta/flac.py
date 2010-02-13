import mutagen.flac
import logging


_logger = logging.getLogger();

_flac2common = {
    "ALBUM"       : "album_title",
    "ALBUMARTIST" : "album_artist",
    "ARTIST"      : "artist",
    "COMPOSER"    : "composer",
    "DATE"        : "date",
    "DISCNUMBER"  : "disc_number",
    "DISCTOTAL"   : "disc_total",
    "GENRE"       : "genre",
    "ISRC"        : "isrc",
    "TITLE"       : "title",
    "TRACKNUMBER" : "track_number",
    "TRACKTOTAL"  : "track_total"
    }

def recognized( fileAbs ):
    fileObj = file(fileAbs)
    fileHeader = fileObj.read(128)
    matchScore = mutagen.flac.FLAC.score( fileAbs, fileObj, fileHeader )
    return matchScore > 0

class FlacFile():
    def __init__( self, flacFileAbs ):
        self.flacObj = mutagen.flac.FLAC( flacFileAbs )

    def getTags( self ):
        commonTags = {}

        for flacTagName, value in self.flacObj.items():
            try:
                commonTagName = _flac2common[ flacTagName.upper() ]            
            except KeyError:
                _logger.warn("Common mapping for flac tag '%s' not found" % flacTagName)
                continue

            if commonTagName.endswith("total") or commonTagName.endswith("number"):
                commonTags[commonTagName] = int(value[0])
            else:
                unicodeValues = [unicode(x) for x in value]
                commonTags[commonTagName] = unicodeValues

        return commonTags
