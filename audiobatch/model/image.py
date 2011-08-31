import StringIO

SUBJECT__ALBUM_COVER = "cover"
from PIL import Image

def makeImage( path=None, bytes=None ):
    from audiobatch.persistence import imagefile
    return imagefile.LazyPILImage( path, bytes )


class Image( object ):

    def get_bytes( self ):
        raise NotImplementedError

    def get_dimensions( self ):
        raise NotImplementedError

    def get_mime_type( self, shorten=False ):
        raise NotImplementedError

    def conform_size( self, max_side_length ):
        raise NotImplementedError

class ImageRef( object ):
    def open():
        raise NotImplementedError        