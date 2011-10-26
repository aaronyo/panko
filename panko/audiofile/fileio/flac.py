from mutagen import flac
from . import fileio

EXTENSIONS = ['flac']

class FLACIO( fileio.FileIO ):
    kind = 'flac'

    def __init__(self, path):
        self.path = path
        super(FLACIO, self).__init__( flac.FLAC(path) )

    def set_tag(self, location, value):
        value = [unicode(v) for v in value]
        self.mtg_file[location.key] = value
        
    def get_tag(self, location):
        return self.mtg_file.get(location.key, None)
    
    def get_audio_bytes(self):
        data = open(self.path).read()
        offset = 0
        # looking for flac frame sync code: 1111 1111 1111 10 ??
        offset = data.find("\xff")
        while offset > 0:
            # check that next byte matches 1111 10??
            if ord(data[offset+1]) & 0xfc == 0xf8:
                break
            else:
                offset = data.find("\xff", offset)
                
        # FIXME: use custom exception
        if offset < 0:
            raise Exception('Audio data marker or "synce code" not found')

        return data[offset:]            
            
        
    def cover_art_key(self):
        return None
