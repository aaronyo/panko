from mutagen import mp4
from . import AudioFile

EXTENSIONS = ['m4a', 'mp4']

class MP4File( AudioFile ):
    
    kind = 'MP4'
    _mutagen_class = mp4.MP4

    def _tag_mapping(self):
        return self._tag_mapping_dict

    def _part_of(mp4_tag_name, idx):
        def to_box(value, mp4_obj):
            #FIXME: None does not work?
            if mp4_tag_name in mp4_obj:
                parts = list(mp4_obj[mp4_tag_name][0])
            else:
                parts = [0,0]
            parts[idx] = value
            mp4_obj[ mp4_tag_name ]= [ parts ]
        def from_box(mp4_obj):
            if mp4_tag_name in mp4_obj:
                return mp4_obj[mp4_tag_name][0][idx]
        return mp4_tag_name, to_box, from_box

    # reference: http://code.google.com/p/mp4v2/wiki/iTunesMetadata#Sources
    _tag_mapping_dict = {
        "album.artists"      : "aART",
        "album.title"        : "\xa9alb",
        "album.release_date" : "\xa9day",
        "artists"            : "\xa9ART",
        "composers"          : "\xa9wrt",
        "disc_number"        : _part_of('disk', 0),
        "disc_total"         : _part_of('disk', 1),
        "track_number"       : _part_of('trkn', 0),
        "track_total"        : _part_of('trkn', 1),
        "genres"             : "\xa9gen",
        "title"              : "\xa9nam",
        # Non standard tags.  (iTunes is the defactor standard)
        # FIXME: what does dbPoweramp use?
        "isrc"               : "----:com.apple.iTunes:ISRC"
    }

    def has_cover_art(self):
        # FIXME: implement
        return False
