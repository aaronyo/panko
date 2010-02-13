import os.path
import flacmeta
import mp3meta
import m4ameta
from PIL import Image

IMAGE_SUBJECT__ALBUM_COVER = "album_cover"

class AudioMeta:

    def __init__( self ):
        self.tags = {}
        self.images = {}
        self.imageOutputEncoding="jpeg"

    def readFile( self, audioFileAbs, tags=True, images=False ):
        audioFileObj = AudioMeta._constructAudioFile( audioFileAbs )        

        if tags:
            self.tags.update( audioFileObj.getTags() )
        if images:
            raise Exception("Extracting images from an audio file is not yet supported")
            
    def writeFile( self, audioFileAbs, clearFirst=False, tags=True, images=True ):
        audioFileObj = AudioMeta._constructAudioFile( audioFileAbs )

        if clearFirst:
            audioFileObj.clearAll()
        if tags:
            audioFileObj.setTags( self.tags )
        if images:
            audioFileObj.setImages( self.images, self.imageOutputEncoding )

        audioFileObj.save()

    def addImage( self, imageFileAbs, maxSideLength=None, subject=None ):
        filename = os.path.basename( imageFileAbs )
        if subject == None:
            if filename.startswith("cover"):
                subject = IMAGE_SUBJECT__ALBUM_COVER
            else:
                raise Exception( "Unable to determine image subject from filename: %s" % imageFileAbs )

        image = Image.open( imageFileAbs )
        if maxSideLength != None:
            image = AudioMeta._conformSize( image, maxSideLength )
            
        self.images[subject] = image

        
    @staticmethod
    def _constructAudioFile( audioFileAbs ):
        if flacmeta.recognized( audioFileAbs ):
            return flacmeta.FlacFile( audioFileAbs )
        elif mp3meta.recognized( audioFileAbs ):
            return mp3meta.Mp3File( audioFileAbs )
        elif m4ameta.recognized( audioFileAbs ):
            return m4ameta.M4aFile( audioFileAbs )
        else:
            raise Exception( "File type not recognized for file: %s" % audioFileAbs )

    @staticmethod
    def _conformSize( image, maxSideLength ):
        width, height = image.size
        if width >= height:
            if width > maxSideLength:
                targetWidth = maxSideLength
                targetHeight = int( (float(targetWidth) / width) * height )
        else:
            if height > maxSideLength:
                targetHeight = maxSideLength
                targetWidth = int ( (float(targetHeight) / height) * width )
        
        if targetWidth != None:
            return image.resize( (targetWidth, targetHeight), Image.ANTIALIAS )
        else:
            # both return cases should behave the same concerning making a copy rather than returning
            # a ref to the same object
            return copy.deepcopy(image)
