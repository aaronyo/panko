from datetime import datetime
import os
import stat
import collections
import logging

from . import tagmap
from .fileio import mp3, flac, mp4
from . import albumart
from .flexdatetime import FlexDateTime
from .. import util

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
            file_io_class = mp3.MP3IO
        elif self.ext in flac.EXTENSIONS:
            file_io_class = flac.FLACIO
        elif self.ext in mp4.EXTENSIONS:
            file_io_class = mp4.MP4IO
            
        self.loc_map = tag_map.locations[file_io_class.kind]
        self.type_map = tag_map.tag_types
            
        self.kind = file_io_class.kind
        self.file_io = file_io_class(self.path)
        self._dirty = False
    
    @property
    def has_folder_cover(self):
        return self.folder_cover_path != None
    
    @property
    def has_embedded_cover(self):
        return self.file_io.cover_art_key() != None

    def embed_cover(self, art):
        self._dirty = True
        self.file_io.set_cover_art(art.bytes, art.mime_type)
        
    def extract_cover(self):
        bytes, mime_type = self.file_io.get_cover_art()
        return albumart.AlbumArt(bytes, mime_type)
    
    def __del__(self):
        self.flush()
    
    def close(self):
        self.flush()
        del self.file_io
            
    def flush(self):
        if self._dirty:
            self.file_io.save()
            self._dirty = False
        
    def read_tags(self):
        return dict((name, value) for name, _, value in self.read_extended_tags())

    def clear_tags(self):
        self._dirty=True
        self.file_io.clear_tags()
    
    def write_tags(self, tags):
        self._dirty = True
        cur_rows = self.read_extended_tags()
        locations = dict((tag_name, location) for tag_name, location, _ in cur_rows)
        for name, value in tags.items():
            value = util.seqify(value)
            if not self.type_map[name].is_multival:
                value = [value[0]]
            value = [str(item) if isinstance(item, FlexDateTime) else item for item in value ] 
            if name in locations:
                self.file_io.set_tag(locations[name], value)
            elif name in self.loc_map:
                self.file_io.set_tag(self.loc_map[name][0], value)
            else:
                _logger.error("unable to save %s for file '%s': "
                              "location unkown for %s" % (tag_name, self.path, self.kind))
            
    def read_extended_tags(self, keep_unknown=False):
        rows = []
        for key in self.file_io.keys():
            rows.extend( self._lookup(key, keep_unknown) )
        return rows
            
    def _lookup(self, key, keep_unknown=False):
        rows = []
        for tag_name, tag_locs in self.loc_map.items():
            for loc in tag_locs:
                if loc.key == key:
                    data = self.file_io.get_tag(loc)
                    tag_type = self.type_map[tag_name]
                    value = self._parse_tag( tag_type, data )
                    rows.append((tag_name, loc, value))
        if not rows and keep_unknown:
            loc = tagmap.Location(key, None)
            data = self.file_io.get_tag(loc)
            tags[key] = (loc, data)
            rows.append((None, loc, value))
        return rows

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