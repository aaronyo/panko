import PIL
import os

def load(path):
    format = os.path.splitext(path)[1][1:].lower()
    format = 'jpeg' if format == 'jpg' else format
    return AlbumArt(open(path).read(), format)

class AlbumArt( object ):
    def __init__( self, bytes, format ):
        self.bytes = bytes
        if format.startswith('image/'):
            format = format[6:]
        self.format = format.lower()

    def __eq__(self, other):
       return self.bytes == other.bytes and self.format == other.format

    @staticmethod
    def from_pil_image( pil_image, format ):
        buf = StringIO.StringIO()
        pil_image.save(buf, format = format or pil_image.format)
        bytes = buf.getvalue()
        buf.close()
        return AlbumArt(bytes, pil_image.format)
        
    def to_pil_image(self):
        pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
        pil_image.format = self.format
        return pil_image

    def dimensions( self ):
        return self._pil_image().size

    def mime_type( self, shorten=False ):
        return self.format

    def full_mime_type(self):
        return "image/" + self.format.lower()

    def conform_size( self, max_side_length ):
        '''Returns a copy conforming to max_side_length'''
        pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
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
            return Image.from_pil_image( new_pil_image, self.format )
        else:
            return Image( copy.deepcopy(self.bytes), self.format )
