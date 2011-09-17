from mutagen import mp4


EXTENSIONS = ['m4a', 'mp4']


class MP4Translator( object ):
    kind = 'MP4'
    mutagen_class = mp4.MP4
        
    _image_formats = {
        'image/jpeg' : mp4.MP4Cover.FORMAT_JPEG,
        'image/png'  : mp4.MP4Cover.FORMAT_PNG
    }

    def embed_cover_art(self, mp4_obj, bytes, mime_type):
        fmt = self._image_formats[mime_type]
        mp4_obj['covr'] = [mp4.MP4Cover(bytes, fmt)]

    def extract_cover_art(self, mp4_obj):
        art = mp4_obj['covr'][0]
        for mime, mp4_fmt in self._image_formats.items():
            if mp4_fmt == art.imageformat:
                return art, mime

    def has_cover_art(self, mp4_obj):
        return 'covr' in mp4_obj


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

