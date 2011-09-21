from mutagen import mp4
from . import fileio

EXTENSIONS = ['m4a', 'mp4']

class MP4IO( fileio.FileIO ):
    kind = 'mp4'
    default_cover_key = 'covr'      
            
    _image_formats = {
        'image/jpeg' : mp4.MP4Cover.FORMAT_JPEG,
        'image/png'  : mp4.MP4Cover.FORMAT_PNG
    }

    def __init__(self, path):
        self.path = path
        super(MP4IO, self).__init__( mp4.MP4(path) )

    def set_tag(self, location, value):
        key = location.key.replace('(c)', '\xa9')
        if location.part != None:
            data = self.mtg_file.get(key, None)
            new_data = []
            for i, v in enumerate(value):
                parts = data[i] if data and i < len(data) else [0,0]
                parts[location.part] = v
                new_data.append(parts)
            self.mtg_file[key] = new_data
        else:
            self.mtg_file[key] = value
            
        
    def get_tag(self, location):
        key = location.key.replace('(c)', '\xa9')
        data = self.mtg_file.get(key, None)
        if data and location.part != None:
            return([ item[location.part] for item in data ])
        else:
            return data
        
    def cover_art_key(self):
        if self.default_cover_key in self.mtg_file:
            return self.default_cover_key

    def set_cover_art(self, bytes, mime_type):
        key = self.cover_art_key()
        if key:
            art = self.mtg_file[key]
            del art[0]
        else:
            key = self.default_cover_key
            art = []
            
        fmt = self._image_formats[mime_type]
        art.insert(0, mp4.MP4Cover(bytes, fmt))
        self.mtg_file[key] = art

    def get_cover_art(self):
        key = self.cover_art_key()
        if key:
            art = self.mtg_file[key][0]
            for mime, mp4_fmt in self._image_formats.items():
                if mp4_fmt == art.imageformat:
                    return art, mime
        return None, None

    def keys(self):
        return [ k.replace('\xa9', '(c)') for k in self._raw_keys() ]

    def _raw_keys(self):
        return ( k for k in self.mtg_file.keys() if not k == 'covr')
        
    def clear_tags(self):
        # We don't want to delete the cover art
        map(self.mtg_file.__delitem__, self._raw_keys())

    def has_cover_art(self):
        return 'covr' in self.mtg_file