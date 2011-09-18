from mutagen import mp3, id3
from . import fileio


EXTENSIONS = ['mp3']

class MP3IO( fileio.FileIO ):
    kind = 'mp3'
    
    def __init__(self, path):
        super(MP3IO, self).__init__( mp3.MP3(path) )

    def set_tag(self, location, value):
        if location.part != None:
            frame_text = self._get_frame(location.key)
            parts = list(_split_frame_text(frame_text)) if frame_text else [None, None]
            parts[location.part] = value
            value = _join_frame_text(*parts)
        self._set_frame(location.key, value)

    def get_tag(self, location):
        frame_text = self._get_frame(location.key)
        if frame_text and location.part != None:
            parts = _split_frame_text(frame_text)
            frame_text = parts[location.part]
        return frame_text
    
    def embed_cover_art(self, bytes, mime_type):
        id3_cover_art_code = 3
        apicFrame = id3.APIC( encoding = 3,
                              mime = mime_type,
                              type = id3_cover_art_code,
                              desc = 'cover',
                              data = bytes )
        self.mtg_file.tags.add( apicFrame )        

    def extract_cover_art(self):
        apic = None
        for k, v in self.mtg_file.items():
            if isinstance(v, id3.APIC):
                if 'cover' in k.lower():
                    # Good match -- take it
                    return v.data, v.mime
                else:
                    # ok match -- whait and see
                    apic = v
        if apic:
            return apic.data, apic.mime
        else:
            return None, None

    def has_cover_art(self):
        return any( type(v) == id3.APIC for v in self.mtg_file.values() )
        
    def keys(self):
        return [k for k, v in self.mtg_file.items() if not isinstance(k, id3.APIC)]

    def _set_frame(self, frame_name, value):
        print frame_name
        frame_class = _get_frame_class(frame_name)
        frame = frame_class( encoding=3, text=value )
        self.mtg_file.tags.add( frame )

    def _get_frame(self, frame_name):
        if frame_name not in self.mtg_file:
             return None
        return unicode(self.mtg_file[frame_name])            

def _split_frame_text(text):
    vals = text.split("/")
    return vals[0], vals[1] if len(vals) > 1 else None

def _join_frame_text(pos, total):
    if not pos and not total:
        text = None
    else:
        pos = pos or "" 
        total =  "/%s" % total if total else ""
        text = u"%s%s" % ( pos, total )
    return text

def _get_frame_class(frame_name):
    return id3.__dict__[frame_name.split(':')[0]]
