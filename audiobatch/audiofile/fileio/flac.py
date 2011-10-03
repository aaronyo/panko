from mutagen import flac
from . import fileio

EXTENSIONS = ['flac']

class FLACIO( fileio.FileIO ):
    kind = 'flac'

    def __init__(self, path):
        super(FLACIO, self).__init__( flac.FLAC(path) )

    def set_tag(self, location, value):
        value = [unicode(v) for v in value]
        self.mtg_file[location.key] = value
        
    def get_tag(self, location):
        return self.mtg_file.get(location.key, None)
