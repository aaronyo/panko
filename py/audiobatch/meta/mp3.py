from mutagen import mp3
from mutagen import id3 
import logging
import StringIO

_logger = logging.getLogger();

_commonToId3 = {
    "album_title"  : id3.TALB,
    "album_artist" : id3.TPE2,
    "artist"       : id3.TPE1,
    "composer"     : id3.TCOM,
    "date"         : id3.TDRC,
    "disc_number"  : None,  # requires custom handling
    "disc_total"   : None,  # requires custom handling
    "genre"        : id3.TCON,
    "isrc"         : id3.TSRC,
    "title"        : id3.TIT2,
    "track_number" : None, # requires custom handling
    "track_total"  : None, # requires custom handling
}

_imageEncodingToMimeType = {
    "jpeg" : "image/jpeg",
    "png"  : "image/png"
}

_imageSubjectToId3Code = {
    "album_cover" : 3
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


class Mp3File:
    def __init__( self, mp3FileAbs ):
        self.mp3FileAbs = mp3FileAbs
        self.mp3Obj = mp3.MP3( mp3FileAbs )

    def clearAll( self ):
        self.mp3Obj.delete()
        
    def addTags( self, tags ):
        # id3 combines the number and total into a single field of format: "number/total"
        discNumber = None
        discTotal = None
        trackNumber = None
        trackTotal = None

        for tagName, value in tags.items():

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
                    frameClass = _commonToId3[ tagName ]
                except KeyError:
                    _logger.warn("Id3 mapping for common tag '%s' not found.  Will not be written to mp3: %s" \
                                     % (tagName, self.mp3FileAbs) )
                    continue

                frameObj = frameClass(encoding=3, text=value)
                self.mp3Obj[ frameClass.__name__ ] = frameObj

        tposFrame = _makeTposFrame(discNumber, discTotal)
        if tposFrame != None:
            self.mp3Obj[ tposFrame.__class__.__name__ ] = tposFrame
            
        trckFrame = _makeTrckFrame(trackNumber, trackTotal)
        if trckFrame != None:
            self.mp3Obj[ trckFrame.__class__.__name__ ] = trckFrame

    def addImages(self, imageDict, encoding ):
        mimeType = _imageEncodingToMimeType[encoding]
        for subject, image in imageDict.items():
            if _imageSubjectToId3Code.has_key( subject ):
                id3PicCode = _imageSubjectToId3Code[ subject ]
            else:
                _logger.warn("Id3 mapping for image subject '%s' not found.  Will not be written to mp3: %s" \
                                 % (flacTagName, self._mp3FileAbs) )
                continue

            #Image is a PIL Image object.  Get the binary data in encoding of our choice.
            buf = StringIO.StringIO()
            image.save( buf, format=encoding )
            imageData = buf.getvalue()
            buf.close()

            apicFrame = id3.APIC( encoding = 3,
                                  mime = 'image/jpeg',
                                  type = id3PicCode,
                                  desc = u'AlbumCover',
                                  data = imageData )
            self.mp3Obj.tags.add( apicFrame )
            

    def save( self ):
        self.mp3Obj.save()

