from . import AudioFile
from mutagen import flac

EXTENSIONS = ['flac']

class FLACFile( AudioFile ):
    kind = 'MP3'
    _mutagen_class = flac.FLAC

    _tag_mapping_dict = {
        "artists"            : "artist",
        "composers"          : "composer",
        "genres"             : "genre",
        "isrc"               : "isrc",
        "title"              : "title",
        "track_number"       : "tracknumber",
        "track_total"        : "tracktotal",
        "disc_number"        : "discnumber",
        "disc_total"         : "disctotal",
        "album.title"        : "album",
        "album.artists"      : "albumartist",
        "album.release_date" : "date"
    }
    
    def _tag_mapping(self):
        return self._tag_mapping_dict

    def has_cover_art(self):
        # FIXME: implement
        return False