from datetime import datetime
import os
import stat
from . import tagmap
from .fileio import mp3, flac, mp4
import collections

_default_handler = None
def load(file_path):
    global _default_handler
    if not _default_handler:
        _default_handler = AudioFileHandler()
    return _default_handler.load(file_path)

class AudioFileHandler(object):
    
    def __init__(self, config=None):
        if not config:
            self.tag_map = tagmap.load()
        else:
            self.tag_map = tagmap.load(config)
            
    def load(self, path):
        return AudioFile(path, self.tag_map)

MappedTag = collections.namedtuple("MappedTag", "location, value")

class AudioFile( object ):
    
    def __init__(self, path, tag_map):
        self.path = path
        self.mod_time = datetime.fromtimestamp( os.stat(path)[stat.ST_MTIME] )
        _, ext = os.path.splitext( path )
        self.ext = ext[1:] # drop the "."
        if self.ext in mp3.EXTENSIONS:
            self.file_io_class = mp3.MP3IO
        elif self.ext in flac.EXTENSIONS:
            self.file_io_class = flac.FLACIO
        elif self.ext in mp4.EXTENSIONS:
            self.file_io_class = mp4.MP4IO
            
        self.loc_map = tag_map.locations[self.file_io_class.kind]
        self.type_map = tag_map.tag_types
            
        self.kind = self.file_io_class.kind

        self.kind = None
        self.tags = None
        self.locations = None
        self.folder_cover_art = None
        self.embedded_cover_art = None
        self._load()
        
    def rows(self):
        rows_ = [(n, self.locations[n], self.tags[n]) for n in sorted(self.tags)]
        rows_.extend((None, self.unkown_locations[n], self.unkown_tags[n]) for n in sorted(self.unkown_tags))
        return rows_
        
    def _load(self):
        file_io = self.file_io_class(self.path)
        self.tags = {}
        self.locations = {}
        self.unkown_tags = {}
        self.unkown_locations = {}
        for key in file_io.keys():
            is_known, tags = self._lookup(key, file_io)
            if is_known:
                self.tags.update((tag_name, mapping[1]) for tag_name, mapping in tags.items())
                self.locations.update((tag_name, mapping[0]) for tag_name, mapping in tags.items())
            else:
                self.unkown_tags.update((tag_name, mapping[1]) for tag_name, mapping in tags.items())
                self.unkown_locations.update((tag_name, mapping[0]) for tag_name, mapping in tags.items())
        
    def _lookup(self, key, file_io):
        tags = {}
        for tag_name, tag_locs in self.loc_map.items():
            for loc in tag_locs:
                if loc.key == unicode(key, 'latin-1'):
                    text = file_io.get_tag(loc)
                    tag_type = self.type_map[tag_name]
                    value = self._parse_tag( tag_type, text )
                    tags[tag_name] = (loc, value)
        if not tags:
            # get the ascii represantation which will escape non ascii bytes whose
            # encoding we can are not certain of
            loc = tagmap.Location(key, None)
            text = file_io.get_tag(loc)
            tags[key] = (loc, text)
            return False, tags
        else:
            return True, tags

    @staticmethod
    def _parse_tag(tag_type, text):
        if hasattr(text, '__iter__'):
            if tag_type.is_multival:
                return [AudioFile._parse_tag_item(tag_type.type_, i) for i in text]
            else:
                return AudioFile._parse_tag_item(tag_type.type_, text[0])
        else:
            if tag_type.is_multival:
                return [AudioFile._parse_tag_item(tag_type.type_, text)]
            else:
                return AudioFile._parse_tag_item(tag_type.type_, text)           

    @staticmethod
    def _parse_tag_item(type_, value):
        if hasattr(type_, 'parse'):
            parse_func = type_.parse
        else:
            parse_func = type_
        if not value:
            return value
        else:
            return parse_func(unicode(value))        

