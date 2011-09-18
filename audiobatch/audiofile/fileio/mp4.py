from mutagen import mp4
from . import fileio

EXTENSIONS = ['m4a', 'mp4']

class MP4IO( fileio.FileIO ):
    kind = 'mp4'
            
    _image_formats = {
        'image/jpeg' : mp4.MP4Cover.FORMAT_JPEG,
        'image/png'  : mp4.MP4Cover.FORMAT_PNG
    }

    def __init__(self, path):
        super(MP4IO, self).__init__( mp4.MP4(path) )

    def set_tag(self, location, value):        
        key = location.key.replace('(c)', '\xa9')
        if location.part != None:
            if location.name in mp4_obj:
                parts = list(self.mtg_file[key][0])
            else:
                # FIXME: is 0 really equivalent to None here?
                parts = [0,0]
            parts[idx] = value
            value = parts
        self.mtg_file[key]= [value]
        
    def get_tag(self, location):
        key = location.key.replace('(c)', '\xa9')
        if key in self.mtg_file:
            mtg_val = self.mtg_file[key]
            if location.part != None:
                return mtg_val[0][location.part]
            else:
                return mtg_val
        
    def embed_cover_art(self, bytes, mime_type):
        fmt = self._image_formats[mime_type]
        self.mtg_file['covr'] = [mp4.MP4Cover(bytes, fmt)]

    def extract_cover_art(self):
        art = self.mtg_file['covr'][0]
        for mime, mp4_fmt in self._image_formats.items():
            if mp4_fmt == art.imageformat:
                return art, mime

    def keys(self):
        return [ k.replace('\xa9', '(c)') for k, v in self.mtg_file.items()
                 if not (hasattr(v, '__getitem__') and type(v[0]) is mp4.MP4Cover) ]
        
    def has_cover_art(self):
        return 'covr' in self.mtg_file