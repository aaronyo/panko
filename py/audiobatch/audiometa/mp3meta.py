from mutagen import mp3
from mutagen import id3 
import audiometa
import logging


_logger = logging.getLogger();

_commonToMp3 = {
    "album_title"  : id3.TALB,
    "album_artist" : id3.TPE2,
    "artist"       : id3.TPE1,
    "date"         : id3.TDRC,
    "disc_number"  : None,  # requires custom handling
    "disc_total"   : None,  # requires custom handling
    "isrc"         : id3.TSRC,
    "title"        : id3.TIT2,
    "track_number" : None, # requires custom handling
    "track_total"  : None, # requires custom handling
}


def _makeTposFrame( discNumber, discTotal ):
    if discNumber == None:
        return None
    elif discTotal == None:
        frameText = u"%d" % discNumber
    else:
        frameText = u"%d/%d" % ( discNumber, discTotal )

    return id3.TPOS( encoding=3, text=frameText )


def _makeTrckFrame( trackNumber, trackTotal ):
    if trackNumber == None:
        return None
    elif trackTotal == None:
        frameText = u"%d" % trackNumber
    else:
        frameText = u"%d/%d" % ( trackNumber, trackTotal )

    return id3.TRCK( encoding=3, text=frameText )


def recognized( fileAbs ):
    fileObj = file( fileAbs )
    fileHeader = fileObj.read( 128 )
    matchScore = mp3.MP3.score( fileAbs, fileObj, fileHeader )
    return matchScore > 0


def writeCommonTags ( commonTags, mp3FileAbs, clearFirst=False ):

    if not recognized( mp3FileAbs ):
        raise error("File not recognized as valid mp3: %s" % mp3FileAbs)

    mp3Obj = mp3.MP3( mp3FileAbs )
    if clearFirst == True:
        mp3Obj.delete()

    # id3 combines the number and total into a single field of format: "number/total"
    discNumber = None
    discTotal = None
    trackNumber = None
    trackTotal = None

    for tagName, value in commonTags.items():

        if tagName == "disc_number":
            discNumber = value
        elif tagName == "disc_total":
            discTotal = value
        elif tagName == "track_number":
            trackNumber = value
        elif tagName == "track_total":
            trackTotal = value

        else:
            try:
                frameClass = _commonToMp3[ tagName ]
            except KeyError:
                _logger.info("Common mapping for flac tag '%s' not found" % flacTagName)
                continue

            frameObj = frameClass(encoding=3, text=value)
            mp3Obj[ frameClass.__name__ ] = frameObj

    tposFrame = _makeTposFrame(discNumber, discTotal)
    if tposFrame != None:
        mp3Obj[ tposFrame.__class__.__name__ ] = tposFrame

    trckFrame = _makeTrckFrame(trackNumber, trackTotal)
    if trckFrame != None:
        mp3Obj[ trckFrame.__class__.__name__ ] = trckFrame

    mp3Obj.save()

