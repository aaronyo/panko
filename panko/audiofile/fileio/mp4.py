from mutagen import mp4
from . import fileio
from ... import util

# FIXME: try to localize this monkey patch
# Make a hacked version of the module for retrieving the
# audio stream data which mutagen does not support
mp4._CONTAINERS.append('mdat')
# Tried this but didn't work:
# http://stackoverflow.com/questions/7495886/use-a-class-in-the-context-of-a-different-module

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
        self.join_multivalue = True
        self.join_char = '/'

    def set_tag(self, location, value):
        key = location.key.decode('string_escape')
        if key.startswith('----'):
            value = [ unicode(v).encode('utf-8')
                      if hasattr(v, '__unicode__') or isinstance(v, unicode)
                      else str(v) for v in value ]
        if self.join_multivalue:
            value = util.join_items(value, self.join_char)
        if location.part != None:
            data = self.mtg_file.get(key, None)
            new_data = []
            for i, v in enumerate(value):
                parts = list(data[i]) if data and i < len(data) else [0,0]
                parts[location.part] = v
                new_data.append(parts)
            self.mtg_file[key] = new_data
        else:
            self.mtg_file[key] = value
            
        
    def get_tag(self, location):
        key = location.key.decode('string_escape')
        data = self.mtg_file.get(key, None)
        if data and location.part != None:
            return([ item[location.part] for item in data ])
        else:
            if not hasattr(data, '__iter__'):
                return [data]
            else:
                return data
        
    def get_raw(self, key):
        key = key.decode('string_escape')
        return self.mtg_file.get(key, None)

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
        return [ k.encode('string_escape') for k in self._raw_keys() ]

    def _raw_keys(self):
        return ( k for k in self.mtg_file.keys() if not k == 'covr')
        
    def clear_tags(self):
        # We don't want to delete the cover art
        map(self.mtg_file.__delitem__, self._raw_keys())

    def has_cover_art(self):
        return 'covr' in self.mtg_file
        
    def get_audio_bytes(self):
        fileobj = open(self.path, 'r')
        data_atom = mp4.Atoms(fileobj)["mdat"]
        # skip two atom properties: the 4 byte name and the 4 byte length
        offset, length,  = data_atom.offset+8, data_atom.length-8
        fileobj.seek(offset)
        return fileobj.read(length)
