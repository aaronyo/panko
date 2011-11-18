from datetime import datetime
import os
import stat
import collections
import logging
import hashlib

from . import tagmap
from .fileio import mp3, flac, mp4
from . import albumart
from .flexdatetime import FlexDateTime
from .. import util

_logger = logging.getLogger()

_default_handler = None
#FIXME: aboyd: load or open?
def open(path):
    global _default_handler
    if not _default_handler:
        _default_handler = AudioFileHandler()
    return _default_handler.open(path)

def load_folder_art(path, filename):
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
            
    def open(self, path):
        return AudioFile(path, self.tag_map)

class Invalid(object):
    def __str__(self):
        return '<Invalid: Could not parse>'

class AudioFile( object ):
    
    def __init__(self, path, tag_map):
        self._dirty = False
        self.path = path
        self.mod_time = datetime.fromtimestamp( os.stat(path)[stat.ST_MTIME] )
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
    
    def has_folder_cover(self):
        return self.folder_cover_path() != None
    
    def has_embedded_cover(self):
        return self.file_io.cover_art_key() != None
        
    def folder_cover(self):
        path = self.folder_cover_path()
        if path:
            return albumart.load(path)
        
    def folder_cover_path(self, cover_options=['cover.jpg', 'folder.jpg']):
        for filename in cover_options:
            check_path = os.path.join(os.path.dirname(self.path), filename)
            if os.path.exists( check_path ):
                return check_path        

    def embed_cover(self, art, format=None):
        self._dirty = True
        if format and art.format != format:
            art = art.convert(format)
        self.file_io.set_cover_art(art.bytes, art.mime_type)
        
    def extract_cover(self):
        if self.embedded_cover_key():
            bytes, mime_type = self.file_io.get_cover_art()
            return albumart.AlbumArt(bytes, mime_type)

    def embedded_cover_key(self):
        return self.file_io.cover_art_key()
    
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
        return dict((name, value) for name, value, _, _ in self._extended_tags())

    def clear_tags(self):
        self._dirty=True
        self.file_io.clear_tags()
    
    def write_tags(self, tags):
        self._dirty = True
        cur_rows = self._extended_tags()
        locations = dict((tag_name, location) for tag_name, _, location, _ in cur_rows)
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
        rows = sorted(self._extended_tags(keep_unknown), key=lambda r: (r[0], unicode(r[2])))
        # move rows without a common name to the bottom
        for i in range( len(rows) ):
            if rows[0][0] != None:
                # then we've seen the last row without a name
                break
            rows.append(rows.pop(0))
        return rows
        
    def read_audio_bytes(self):
        return self.file_io.get_audio_bytes()

    def audio_md5(self):
        return hashlib.md5(self.file_io.get_audio_bytes()).hexdigest()

    def _extended_tags(self, keep_unknown=False):
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
                    rows.append( (tag_name, value, loc, self.file_io.get_raw(key)) )
        if not rows and keep_unknown:
            loc = tagmap.Location(key, None)
            rows.append( (None, None, loc, self.file_io.get_raw(key)) )
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
                if type(value) not in [bool, float, int, str, unicode]:
                    value = unicode(value)
                if parse_func == bool and isinstance(value, basestring):
                    value = {'1': 1,  'true': 1, 't': 1,
                             '0': 0, 'false': 0, 'f': 0}[ value.lower() ]
                if parse_func == unicode and isinstance(value, str):
                    # assume any raw strings are utf-8 or ascii
                    return unicode(value, 'utf-8')
                return parse_func(value)
            except:
                #FIXME: this needs to be more informative if
                #       any exception is swallowed... and probably
                #       still should not swallow all exceptions as Invalid
                return Invalid()
