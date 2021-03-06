import PIL.Image
import StringIO
import os
import requests

_cached_urls = {}

def load(path):
    format = os.path.splitext(path)[1][1:].lower()
    format = 'jpeg' if format == 'jpg' else format
    return AlbumArt(open(path).read(), format)
    
def load_url(url):
    global _cached_urls
    #FIXME: cache should not grow indefinitely
    if url not in _cached_urls:
        _cached_urls[url] = requests.get(url)
    response = _cached_urls[url]
    return AlbumArt(response.content, response.headers['content-type'])
    
class AlbumArt( object ):
    def __init__( self, bytes, format ):
        self.bytes = bytes
        self.format = self.std_format(format)

    def __eq__(self, other):
       return self.bytes == other.bytes and self.format == other.format

    @staticmethod
    def std_format(format):
        if format.startswith('image/'):
            format = format[6:]
        return format.lower()

    @staticmethod
    def from_pil_image( pil_image, format ):
        buf = StringIO.StringIO()
        format = format or pil_image.format
        pil_image.save(buf, format = format)
        bytes = buf.getvalue()
        buf.close()
        return AlbumArt(bytes, format)
        
    def to_pil_image(self):
        pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
        pil_image.format = self.format
        return pil_image

    def dimensions( self ):
        return self.to_pil_image().size

    @property
    def mime_type(self):
        return "image/" + self.format.lower()
        
    def convert(self, format):
        return self.from_pil_image( self.to_pil_image(), format )

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
            return AlbumArt.from_pil_image( new_pil_image, self.format )
        else:
            return AlbumArt( copy.deepcopy(self.bytes), self.format )

    def __str__(self):
        return "Image = %s, %d bytes" % (self.mime_type, len(self.bytes))