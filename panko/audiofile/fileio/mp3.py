from mutagen import mp3, id3
from . import fileio
from ..tagmap import Location
from ... import util

EXTENSIONS = ['mp3']
_ID3_COVER_ART_CODE = 3

_ID3_V1_POS = -128
_ID3_V1_EXTENDED_POS = _ID3_V1_POS - 227


class MP3IO( fileio.FileIO ):
    kind = 'mp3'
    default_cover_key = 'APIC:cover'
    
    def __init__(self, path):
        super(MP3IO, self).__init__( mp3.MP3(path) )
        self.path = path
        self.join_multivalue = True
        self.join_char = '/'

    def set_tag(self, location, value):
        if self.join_multivalue:
            value = util.join_items(value, self.join_char)
        if location.part != None:
            vals = []
            frame_data = self._get_frame_data(location.key)
            for i, v in enumerate(value):
                item = frame_data[0] if frame_data and i < len(frame_data) else None
                parts = list(_split_frame_text(item)) if item else [None, None]
                parts[location.part] = v
                vals.append(_join_frame_text(*parts))
                self._set_frame_data(location.key, vals)
        else:
            self._set_frame_data(location.key, value)
        

    def get_tag(self, location):
        frame_data = self._get_frame_data(location.key)
        if frame_data and location.part != None:
            return( [ _split_frame_text(item)[location.part]
                     for item in frame_data ] )
        else:
            return frame_data
    
    def set_cover_art(self, bytes, mime_type):
        key = self.cover_art_key()
        if key:
            del mtg_file[key]
        else:
            key = self.default_cover_key
        desc = key.partition(":")[2]
        apicFrame = id3.APIC( encoding = 3,
                              mime = mime_type,
                              type = _ID3_COVER_ART_CODE,
                              desc = desc,
                              data = bytes )
        self.mtg_file.tags.add( apicFrame )        

    def get_cover_art(self):
        key = self.cover_art_key()
        if key:
            art = self.mtg_file[key]
            return art.data, art.mime
        
    def cover_art_key(self):
        for k, v in sorted(self.mtg_file.items()):
            if isinstance(v, id3.APIC) and v.type == _ID3_COVER_ART_CODE:
                return k
        
    def keys(self):
        return [k for k, v in self.mtg_file.items() if not isinstance(v, id3.APIC)]
    
    def get_audio_bytes(self):
        data = open(self.path).read()
        # I believe this should work, as any id3 data, including images, should
        # be sync safe.
        offset = data.find("\xff\xfb")

        # FIXME: use custom exception
        if offset < 0:
            raise Exception('Audio data marker or "synce code" not found')
        
        if data[_ID3_V1_EXTENDED_POS:_ID3_V1_EXTENDED_POS+4] == 'TAG+':
            end = _ID3_V1_EXTENDED_POS
        elif data[_ID3_V1_POS:_ID3_V1_POS+3] == 'TAG':
            end = _ID3_V1_POS
        else:
            end = len(data)
            
        return data[offset:end]

    def _set_frame_data(self, frame_name, value):            
        frame_class = _get_frame_class(frame_name)
        if frame_class == id3.TXXX:
            # Parse the description out of the frame name
            frame = frame_class( encoding=3, desc=frame_name[5:], text=value )
        else:
            frame = frame_class( encoding=3, text=value )
        self.mtg_file.tags.add( frame )

    def _get_frame_data(self, frame_name):
        if frame_name not in self.mtg_file:
             return None
        frame = self.mtg_file[frame_name]
        if hasattr(frame, 'text'):
            return frame.text
        else:
            return frame #[str(frame).encode('string_escape')]
        

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
