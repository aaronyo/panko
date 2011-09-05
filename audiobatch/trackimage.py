import StringIO
import copy
import PIL.Image
import os

from . import model

def read_image(image_ref):
    if isinstance(image_ref, basestring):
        path = image_ref
    elif image_ref.kind == 'path':
        path = image_ref.path
    else:
        raise NotImplementedError
        
    format = os.path.splitext(path)[1][1:].lower()
    format = 'jpeg' if format == 'jpg' else format
    return TrackImage( open(path).read(), format )


class TrackImage( object ):        
    def __init__( self, bytes, format ):
        self.bytes = bytes
        self._pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
        self._pil_image.format = format
    
    @staticmethod
    def from_pil_image( pil_image, format ):
        buf = StringIO.StringIO()
        pil_image.save(buf, format = format or pil_image.format)
        bytes = buf.getvalue()
        buf.close()
        return TrackImage(bytes, pil_image.format)

    def dimensions( self ):
        return self._pil_image().size

    def mime_type( self, shorten=False ):
        return elf._pil_image().format.lower()

    def full_mime_type(self):
        return "image/" + self._pil_image().format.lower()

    def conform_size( self, max_side_length ):
        '''Returns a copy conforming to max_side_length'''
        pil_image = self._pil_image
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
                                              PIL.Image.ANTIALIAS )
            return TrackImage.from_pil_image( new_pil_image, pil_image.format )
        else:
            return TrackImage.from_bytes( copy.deepcopy(self.bytes), pil_image.format )

