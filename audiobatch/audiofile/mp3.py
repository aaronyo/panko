from mutagen import mp3, id3
from . import wrapper


EXTENSIONS = ['mp3']

class MP3Wrapper( wrapper.MutagenWrapper ):
    kind = 'MP3'
    
    def __init__(self, path):
        super(MP3Wrapper, self).__init__( mp3.MP3(path) )

    def set_tag(self, location, value):
        if location.part != None:
            frame_text = _get_frame(location.name)
            parts = list(_split_frame(frame_text)) if frame_text else None, None
            parts[idx] = value
            value = _join_frame_text(frame_class, *parts)
        self._set_frame(value, frame_name, self.mtg_file )

    def get_tag(self, location):
        frame_text = self._get_frame(location.name, self.mtg_file)
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
        art = self.mtg_file[id3.APIC.__name__+':cover']
        return art.data, art.mime

    def has_cover_art(self):
        return id3.APIC.__name__+':cover' in self.mtg_file

    def _set_frame(self, value, frame_name):
        frame_class = id3.__dict__[frame_name]
        frame = frame_class( encoding=3, text=value )
        self.mtg_file.tags.add( frame )

    def _get_frame(self, frame_name, mtg_file):
        if frame_name not in mtg_file:
             return None
        return unicode(self.mtg_file[frame_name])            

def _split_frame_text(text):
    vals = text.split("/")
    return vals[0], vals[1] if len(vals) > 1 else None

def _join_frame_text(frame_class, pos, total):
    if not pos and not total:
        text = None
    else:
        pos = pos or "" 
        total =  "/%s" % total if total else ""
        text = u"%s%s" % ( pos, total )
    return text

