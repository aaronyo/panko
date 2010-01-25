import mutagen.flac
import audiometa
import logging


_logger = logging.getLogger();

_flac2common = {
    "ALBUM"       : "album_title",
    "ALBUMARTIST" : "album_artist",
    "ARTIST"      : "artist",
    "DATE"        : "date",
    "DISCNUMBER"  : "disc_number",
    "DISCTOTAL"   : "disc_total",
    "ISRC"        : "isrc",
    "TITLE"       : "title",
    "TRACKNUMBER" : "track_number",
    "TRACKTOTAL"  : "track_total"
    }


def extractCommonTags ( flacFileAbs ):

    flacObj = mutagen.flac.FLAC( flacFileAbs )
    commonTags = {}

    for flacTagName, value in flacObj.items():
        try:
            commonTagName = _flac2common[ flacTagName.upper() ]            
        except KeyError:
            _logger.info("Common mapping for flac tag '%s' not found" % flacTagName)
            continue

        commonTags[commonTagName] = value

    return commonTags


def recognized( fileAbs ):
    fileObj = file(fileAbs)
    fileHeader = fileObj.read(128)
    matchScore = mutagen.flac.FLAC.score( fileAbs, fileObj, fileHeader )
    return matchScore > 0
        
