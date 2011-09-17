from datetime import datetime
import os
import stat
from . import tagmap
from . import mp3
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
        self.loc_map = tag_map.locations[self.ext]
        self.type_map = tag_map.tag_types
        if self.ext in mp3.EXTENSIONS:
            self.mtg_wrapper_class = mp3.MP3Wrapper
        self.kind = self.mtg_wrapper_class.kind

        self.kind = None
        self.tags = None
        self.locations = None
        self.folder_cover_art = None
        self.embedded_cover_art = None
        self._load()
        
    def pretty(self):
        def pretty_value(value):
            if hasattr(value, '__iter__'):
                return u", ".join([pretty_value(v) for v in value])
            elif isinstance(value, basestring):
                return u'"%s"' % value
            else:
                return unicode(value)

        rows = [(n, unicode(self.locations[n]), pretty_value(self.tags[n])) for n in sorted(self.tags)]
        rows.extend(('(unkown)', unicode(self.unkown_locations[n]), pretty_value(self.unkown_tags[n])) for n in sorted(self.unkown_tags))
        lengths = [(len(c), len(r), len(v)) for c, r, v in rows]
        col_lengths = zip(*lengths)
        pad = [ max(l)+1 for l in col_lengths ]
        pretty_str = u""
        for row in rows:
            pretty_str += u"%-*s: %-*s: %s\n" \
                % (pad[0], row[0], pad[1], row[1], row[2])
        return pretty_str
        
    def _load(self):
        mtg_wrapper = self.mtg_wrapper_class(self.path)
        self.tags = {}
        self.locations = {}
        self.unkown_tags = {}
        self.unkown_locations = {}
        for loc_name in mtg_wrapper.keys():
            is_known, tags = self._lookup(loc_name, mtg_wrapper)
            if is_known:
                self.tags.update((tag_name, mapping[1]) for tag_name, mapping in tags.items())
                self.locations.update((tag_name, mapping[0]) for tag_name, mapping in tags.items())
            else:
                self.unkown_tags.update((tag_name, mapping[1]) for tag_name, mapping in tags.items())
                self.unkown_locations.update((tag_name, mapping[0]) for tag_name, mapping in tags.items())
        
    def _lookup(self, loc_name, mtg_wrapper):
        tags = {}
        for tag_name, tag_locs in self.loc_map.items():
            for loc in tag_locs:
                if loc.name == loc_name:
                    text = mtg_wrapper.get_tag(loc)
                    tag_type = self.type_map[tag_name]
                    value = self._parse_tag( tag_type, text )
                    tags[tag_name] = (loc, value)
        if not tags:
            # get the ascii represantation which will escape non ascii bytes whose
            # encoding we can are not certain of
            tag_name = 'UNKNOWN:%s' % loc_name
            loc = tagmap.Location(loc_name, None)
            text = mtg_wrapper.get_tag(loc)
            tags[tag_name] = (loc, text)
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

