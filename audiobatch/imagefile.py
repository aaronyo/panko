import StringIO
import copy
import PIL

from audiobatch.util.cache import LRUCache
from audiobatch import model

# Cache up to 100 PIL Image files
_open_images = LRUCache( 100 )

def open(path):
    pil_image = PIL.Image.open( path )
    return PILBasedImage( pil_image )
    
def from_bytes(bytes):
    buf = StringIO.StringIO()
    buf.write( bytes )
    # move the current position back to 0 for PIL's loading
    buf.seek( 0 )
    pil_image = Image.open( buf )
    pil_image.load()
    buf.close()
    return PILBasedImage( pil_image )

class PathImageRef( ImageRef ):
    def __init__(self, path):
        self._path=path
    def open():
        return PILBasedImage.open(path)

class PILBasedImage( model.image.Image ):
    """ Implements the generic AlbumImage interface in a lazy manner. """
        
    def __init__( self, pil_image ):
        self._pil_image = pil_image
        
    def bytes( self ):
        buf = StringIO.StringIO()
        pil_image.save( buf, format = pil_image.format  )
        bytes = buf.getvalue()
        buf.close()
        return bytes

    def dimensions( self ):
        return self._get_pil_image().size

    def mime_type( self, shorten=False ):
        short_mime_type = self._get_pil_image().format.lower()
        if shorten:
            return mime_type
        else:
            return "image/" + short_mime_type

    def conform_size( self, max_side_length ):
        pil_image = self._pil_imag
        width, height = pil_image.size
        if width >= height:
            if width > max_side_length:
                target_width = max_side_length
                target_height = int( (float(target_width) / width) * height )
        elif height > max_side_length:
            target_height = max_side_length
            target_width = int ( (float(target_height) / height) * width )
        
        if target_width != None:
            new_pil_image = pil_image.resize( (target_width, target_height),
                                              Image.ANTIALIAS )
        else:
            # When returning a copy of an Image, we want to copy
            # the actual image bytes, too, to avoid unexpected changes
            #FIXME: test that this actually deepcopies the bytes
            new_pil_image = copy.deepcopy( pil_image )

        # format gets lost when we don't originate a PIL Image from file
        new_pil_image.format = pil_image.format
        return PILBasedImage( new_pil_image )