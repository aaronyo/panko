from datetime import datetime
import os
import stat
import collections
import logging

from . import tagmap
from .fileio import mp3, flac, mp4
from . import albumart
from .flexdatetime import FlexDateTime

_logger = logging.getLogger()

_default_handler = None
#FIXME: aboyd: load or open?
def load(path, cover_art=None):
    global _default_handler
    if not _default_handler:
        _default_handler = AudioFileHandler()
    return _default_handler.load(path, cover_art)

def load_folder_art(path, filename=None):
    dir_ = os.path.dirname(path)
    img_path = os.path.join(dir_, filename)
    if not os.path.exists(img_path):
        return None
    return albumart.load(img_path)

class AudioFileHandler(object):
    
    def __init__(self, config=None):
        if not config:
            self.tag_map = tagmap.load()
        else:
            self.tag_map = tagmap.load(config)
            
    def load(self, path, cover_art=None):
        return AudioFile(path, self.tag_map, cover_art)

MappedTag = collections.namedtuple("MappedTag", "location, value")

class Invalid(object):
    def __str__(self):
        return '<Invalid: Could not parse>'

class AudioFile( object ):
    
    def __init__(self, path, tag_map, cover_art=None):
        self.path = path
        self.mod_time = datetime.fromtimestamp( os.stat(path)[stat.ST_MTIME] )
        self.folder_cover_path = None
        if cover_art:
            check_path = os.path.join(os.path.dirname(path), cover_art)
            if os.path.exists( check_path ):
                self.folder_cover_path = check_path
                
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
        self.embedded_cover_key = None
        self._embedded_cover = None
        file_io = self.file_io_class(self.path)
        self._load_tags(file_io)
        self._discover_art(file_io)
        
    def rows(self):
        rows_ = [(n, self.locations.get(n, None), self.tags[n]) for n in sorted(self.tags)]
        rows_.extend((None, self.unkown_locations.get(n, None), self.unkown_tags[n]) for n in sorted(self.unkown_tags))
        return rows_
    
    @property
    def has_folder_cover(self):
        return self.folder_cover_path != None
    
    @property
    def has_embedded_cover(self):
        return self.embedded_cover_key != None

    def embed_cover(self, art):
        self._embedded_cover = art
        if not self.embedded_cover_key:
            self.embedded_cover_key = self.file_io_class.default_cover_key
        
    def extract_cover(self):
        if self.has_embedded_cover:
            if self._embedded_cover:
                return self._embedded_cover_art
            else:
                file_io = self.file_io_class(self.path)
                bytes, mime_type = file_io.get_cover_art()
                return albumart.AlbumArt(bytes, mime_type)
        
    def save(self):        
        art = self._embedded_cover
        assert(self.embedded_cover_key or not art)
        file_io = self.file_io_class(self.path)
        file_io.clear_tags()
        for tag_name, location, value in self.rows():
            if tag_name:
                if not self.type_map[tag_name].is_multival:
                    value = [value[0]]
                if type(value[0]) == FlexDateTime:
                    value = [str(v) for v in value]
            if not location:
                location = self.loc_map.get(tag_name, [None])[0]
            if location:
                file_io.set_tag(location, value)
            else:
                _logger.warn("unable to save %s for file '%s%': "
                             "location unkown for %s" % (tag_name, self.path, self.kind))    
        if art:
            file_io.set_cover_art(art.bytes, art.mime_type)
        file_io.save()
        
    def _discover_art(self, file_io):
        self.embedded_cover_key = file_io.cover_art_key()
        
    def _load_tags(self, file_io):
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
                if loc.key == key:
                    data = file_io.get_tag(loc)
                    tag_type = self.type_map[tag_name]
                    value = self._parse_tag( tag_type, data )
                    tags[tag_name] = (loc, value)
        if not tags:
            # get the ascii represantation which will escape non ascii bytes whose
            # encoding we are not certain of
            loc = tagmap.Location(key, None)
            data = file_io.get_tag(loc)
            tags[key] = (loc, data)
            return False, tags
        else:
            return True, tags

    @staticmethod
    def _parse_tag(tag_type, text):
        if hasattr(text, '__iter__'):
            return [AudioFile._parse_tag_item(tag_type.type_, i) for i in text]
        else:
            return [AudioFile._parse_tag_item(tag_type.type_, text)]

    @staticmethod
    def _parse_tag_item(type_, value):
        if hasattr(type_, 'parse'):
            parse_func = type_.parse
        else:
            parse_func = type_
        if not value:
            return value
        else:
            # Get rid of Mutagen types before parsing, but
            # don't convert binary strings to unicode
            try:
                if isinstance(value, basestring):
                    return parse_func(value)
                else:
                    return parse_func(unicode(value))
            except:
                #FIXME: this needs to be more informative if
                #       any exception is swallowed... and probably
                #       still should not swallow all exceptions as Invalid
                return Invalid()