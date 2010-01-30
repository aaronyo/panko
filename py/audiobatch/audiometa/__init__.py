import os.path
import flacmeta
import mp3meta
from PIL import Image

IMAGE_SUBJECT_ALBUM_COVER = 3

class AudioMeta:

    def __init__( self ):
        self.tags = {}
        self.images = {}

    def readFile( self, audioFileAbs, tags=True, images=False ):
        audioFileObj = AudioMeta._constructAudioFile( audioFileAbs )        

        if tags:
            self.tags.update( audioFileObj.getTags() )
        if images:
            raise error("Extracting images from an audio file is not yet supported")
            
    def writeFile( self, audioFileAbs, clearFirst=False ):
        audioFileObj = AudioMeta._constructAudioFile( audioFileAbs )
        if clearFirst:
            audioFileObj.clearAll()
        audioFileObj.setTags( self.tags )
        audioFileObj.save()

    def addImage( self, imageFileAbs, maxSideLength=None, encoding="jpg", imageSubject=None ):
        filename = os.path.basename(picFileAbs)
        if imageType == None:
            if filename.startswith("cover"):
                imageType = IMAGE_SUBECT_ALBUM_COVER
            else:
                raise error( "Unable to determine image subject from filename: " % fileName )

        image = Image.open( imageFileAbs )
        if maxSideLength != None:
            image = AudioMeta._conformSize( image, maxSideLength )
            
        self.images[imageType] = image

        
    @staticmethod
    def _constructAudioFile( audioFileAbs ):
        if flacmeta.recognized( audioFileAbs ):
            return flacmeta.FlacFile( audioFileAbs )
        elif mp3meta.recognized( audioFileAbs ):
            return mp3meta.Mp3File( audioFileAbs )
        else:
            raise error( "could not recognize file type: %s" % audioFileAbs )

    @staticmethod
    def _conformSize( image, maxSideLength ):
        width, height = image.size
        if width >= height:
            if width > maxSideLength:
                targetWidth = maxSideLength
                targetHeight = int( (targetWidth / width) * height )
        if height >= width:
            if height > maxSideLength:
                targetHeight = maxSideLength
                targetWidth = int ( (targetHeight / height) * width )
        
        if targetWidth != None:
            return image.resize( (targetWidth, targetHeight), Image.ANTIALIAS )
        else:
            # both return cases should behave the same concerning making a copy rather than returning
            # a ref to the same object
            return copy.deepcopy(image)
