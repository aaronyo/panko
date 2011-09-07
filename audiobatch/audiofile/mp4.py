from mutagen import mp4
from . import AudioFile


EXTENSIONS = ['m4a', 'mp4']


class MP4File( AudioFile ):
    kind = 'MP4'
    _mutagen_class = mp4.MP4

    def _tag_mapping(self):
        # reference: http://code.google.com/p/mp4v2/wiki/iTunesMetadata#Sources
        return {
            "album.artists"      : "aART",
            "album.title"        : "\xa9alb",
            "album.release_date" : "\xa9day",
            "artists"            : "\xa9ART",
            "composers"          : "\xa9wrt",
            "disc_number"        : _part(0, 'disk'),
            "disc_total"         : _part(1, 'disk'),
            "track_number"       : _part(0, 'trkn'),
            "track_total"        : _part(1, 'trkn'),
            "genres"             : "\xa9gen",
            "title"              : "\xa9nam",
            # Non standard tags.  (btw, standards for mp4 = what iTunes does)
            # FIXME: what does dbPoweramp use when writing isrc?
            "isrc"               : "----:com.apple.iTunes:ISRC"
        }
        
    _image_formats = {
        'image/jpeg' : mp4.MP4Cover.FORMAT_JPEG,
        'image/png'  : mp4.MP4Cover.FORMAT_PNG
    }

    def _embed_cover_art(self, bytes, mime_type):
        fmt = self._image_formats[mime_type]
        self._mutagen_obj['covr'] = [mp4.MP4Cover(bytes, fmt)]

    def _extract_cover_art(self):
        art = self._mutagen_obj['covr'][0]
        for mime, mp4_fmt in self._image_formats.items():
            if mp4_fmt == art.imageformat:
                return art, mime

    def has_cover_art(self):
        return 'covr' in self._mutagen_obj.tags


def _part(idx, mp4_tag_name):
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

