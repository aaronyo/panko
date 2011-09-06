from mutagen import mp3, id3
import logging
import StringIO
import shutil

from . import AudioFile
from audiobatch.model import track

_LOGGER = logging.getLogger()


EXTENSIONS = ['mp3']

class MP3File( AudioFile ):
    
    kind = 'MP3'
    _mutagen_class = mp3.MP3
    
    def _tag_mapping(self):
        return self._tag_mapping_dict
    
    def _embed_cover_art(self, bytes, mime_type):
        id3_cover_art_code = 3
        apicFrame = id3.APIC( encoding = 3,
                              mime = mime_type,
                              type = id3_cover_art_code,
                              desc = 'cover',
                              data = bytes )
        self._mutagen_obj.tags.add( apicFrame )        

    def _extract_cover_art(self):
        art = self._mutagen_obj[id3.APIC.__name__+':cover']
        return art.data, art.mime

    def has_cover_art(self):
        return id3.APIC.__name__+':cover' in self._mutagen_obj

    def _frame(frame_class):
        frame_name = frame_class.__name__
        def to_frame(value, mp3_obj):
            frame = frame_class( encoding=3, text=value )
            mp3_obj.tags.add( frame )            
        def from_frame(mp3_obj):
            if frame_name not in mp3_obj:
                 return None
            return mp3_obj[frame_class.__name__].text            
        return frame_name, to_frame, from_frame
        
    def _part_of_frame(frame_class, idx):
        frame_name = frame_class.__name__

        def _split_frame(frame):
            if not frame:
                return None, None
            vals = frame.text[0].split("/")
            return vals[0], vals[1] if len(vals) > 1 else None

        def _join_frame(frame_class, pos, total):
            if not pos and not total:
                text = None
            else:
                pos = pos or "" 
                total =  "/%s" % total if total else ""
                text = u"%s%s" % ( pos, total )
            return frame_class( encoding=3, text=text ) if text else None

        def to_frame(value, mp3_obj):
            parts = list( _split_frame(mp3_obj.get(frame_name, None)) )
            parts[idx] = value
            frame = _join_frame(frame_class, *parts)
            mp3_obj.tags.add(frame)
        def from_frame(mp3_obj):
            if frame_name not in mp3_obj:
                 return None
            parts = _split_frame(mp3_obj[frame_name])
            print 'parts %s' % str(parts)
            return parts[idx]
        return frame_name, to_frame, from_frame
        
    _tag_mapping_dict = {
        "artists"            : _frame(id3.TPE1),
        "composers"          : _frame(id3.TCOM),
        "genres"             : _frame(id3.TCON),
        "isrc"               : _frame(id3.TSRC),
        "title"              : _frame(id3.TIT2),
        "track_number"       : _part_of_frame(id3.TRCK, 0),
        "track_total"        : _part_of_frame(id3.TRCK, 1),
        "disc_number"        : _part_of_frame(id3.TPOS, 0),
        "disc_total"         : _part_of_frame(id3.TPOS, 1),
        "album.title"        : _frame(id3.TALB),
        "album.artists"      : _frame(id3.TPE2),
        "album.release_date" : _frame(id3.TDRC)
    }


