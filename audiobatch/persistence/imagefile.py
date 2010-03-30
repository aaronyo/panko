import StringIO
import copy
from PIL import Image

from audiobatch.util.cache import LRUCache
from audiobatch import model

# Cache up to 100 PIL Image files
_open_images = LRUCache( 100 )

def _get_pil_image( path ):
    try:
        image = _open_images[ path ]
    except KeyError:
        image = Image.open( path )
        _open_images[ path ] = image

    return image


class LazyPILImage( model.image.Image ):
    """ Implements the generic AlbumImage interface in a lazy manner. """
    
    def __init__( self, path=None, bytes=None, pil_image=None ):

        if path == None and bytes == None and pil_image == None:
            raise ValueError( "must specify 'path', 'bytes' or 'pil_image'" )
        # If we construct with a path, we'll leverage the LRUCache for
        # referencing the PIL image.  The PIL image is never loaded unless
        # details of the image are actually asked for.  This allows us to
        # construct many "lazy" Image instances (e.g. when loading up your full
        # track library) withouth incurring any performance or memory
        # penalty.
        self._path = path

        # If we construct with a pil_image, this instance is probably
        # derivative, e.g. the product of a "conform_size()" call.  At this
        # point, not worried about having lots of these derivatives in
        # memory, so we won't worry about pushing to a temp file, etc.
        if pil_image != None:
            self._pil_image = pil_image

        # When an embedded image is extracted from an audio file, it will
        # come as encoded (e.g. jpg) bytes.  Would be easy to cache these,
        # keeping around the path to the source audio file, but not that
        # optimization can wait.
        elif bytes != None:
            self._pil_image = LazyPILImage._bytes_to_pil_image( bytes )
        else:
            self._pil_image = None
        
    def get_bytes( self ):
        return LazyPILImage._pil_image_to_bytes( self._get_pil_image() )

    def get_dimensions( self ):
        return self._get_pil_image().size

    def get_mime_type( self, shorten=False ):
        short_mime_type = self._get_pil_image().format.lower()
        if shorten:
            return mime_type
        else:
            return "image/" + short_mime_type

    def conform_size( self, max_side_length ):
        pil_image = self._get_pil_image()
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
        return LazyPILImage( pil_image = new_pil_image )

    def _get_pil_image( self ):
        if self._pil_image != None:
            return self._pil_image
        else:
            return _get_pil_image( self._path )

    @staticmethod
    def _bytes_to_pil_image( bytes ):
        buf = StringIO.StringIO()
        buf.write( bytes )
        # move the current position back to 0 for PIL's loading
        buf.seek( 0 )
        pil_image = Image.open( buf )
        pil_image.load()
        buf.close()
        return pil_image

    @staticmethod
    def _pil_image_to_bytes( pil_image ):
        buf = StringIO.StringIO()
        pil_image.save( buf, format = pil_image.format  )
        bytes = buf.getvalue()
        buf.close()
        return bytes
