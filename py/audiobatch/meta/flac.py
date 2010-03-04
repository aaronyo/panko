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

_common2flac = dict((value,key) for key, value in _flac2common.iteritems())

def recognized( fileAbs ):
    fileObj = file(fileAbs)
    fileHeader = fileObj.read(128)
    matchScore = mutagen.flac.FLAC.score( fileAbs, fileObj, fileHeader )
    return matchScore > 0

class FlacFile():
    def __init__( self, flacFileAbs ):
        self.flacObj = mutagen.flac.FLAC( flacFileAbs )
        self.flacFileAbs = flacFileAbs

    @property
    def bitrate(self):
        # Mutagen does not provide bitrate for Flac
        # FIXME
        return 900000

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

    def addTags( self, tags ):
        for tagName, tagValue in tags.items():

            try:
                flacTagName =  _common2flac[tagName]
            except KeyError:
                _logger.warn("Flac mapping for common tag '%s' not found.  Will not be written to flac: %s" \
                                     % (flacTagName, self.flacFileAbs) )
                continue

            self.flacObj[ flacTagName ] = tagValue

    def save( self ):
        self.flacObj.save()
