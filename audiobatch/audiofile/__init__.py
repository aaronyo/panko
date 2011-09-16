from datetime import datetime
import os
import stat
from . import translation
from . import mp3

_default_handler = None
def load(file_path):
    global _default_handler
    if not _default_handler:
        _default_handler = AudioFileHandler()
    return _default_handler.load(file_path)
    

class AudioFileHandler(object):
    
    def __init__(self, config=None):
        if not config:
            self.translation_spec = translation.load()
        else:
            self.translation_spec = translation.load()
            
    def load(self, path):
        return AudioFile(path, self.translation_spec)

class AudioFile( object ):
    
    def __init__(self, path, translation_spec):
        self.path = path
        self.mod_time = datetime.fromtimestamp( os.stat(path)[stat.ST_MTIME] )
        _, ext = os.path.splitext( path )
        self.ext = ext[1:] # drop the "."
        self.loc_specs = translation_spec.location_specs[self.ext]
        self.type_specs = translation_spec.type_specs
        if self.ext in mp3.EXTENSIONS:
            self.mtg_wrapper_class = mp3.MP3Wrapper
        self.kind = self.mtg_wrapper_class.kind

        self.kind = None
        self.tags = None
        self.raw_tags = None
        self.folder_cover_art = None
        self.embedded_cover_art = None
        self._load()
        
    def _load(self):
        mtg_wrapper = self.mtg_wrapper_class(self.path)
        matches = {}
        for raw_name in mtg_wrapper.keys():
            matches.update( self._lookup(raw_name, mtg_wrapper) )
        self.tags = matches
        
    def _lookup(self, raw_name, mtg_wrapper):
        matches = {}
        for tag_name, loc_specs in self.loc_specs.items():
            for loc_spec in loc_specs:
                if loc_spec.raw_name == raw_name:
                    raw_value = mtg_wrapper.get_tag(loc_spec)
                    type_spec = self.type_specs[tag_name]
                    value = self._parse_raw_tag( type_spec, raw_value )
                    matches[tag_name] = (loc_spec, raw_value)
        if not matches:
            # get the ascii represantation which will escape non ascii bytes whose
            # encoding we can are not certain of
            tag_name = 'UNKNOWN:%s' % raw_name.__repr__()[1:-1]
            loc_spec = translation.LocationSpec(raw_name, None)
            raw_value = mtg_wrapper.get_tag(loc_spec)
            matches[tag_name] = (loc_spec, raw_value)
        return matches

    @staticmethod
    def _parse_raw_tag(type_spec, value):
        if type_spec.is_multival:
            return [AudioFile._parse_tag_item(type_spec.type_, v) for v in value]
        else:
            return AudioFile._parse_tag_item(type_spec.type_, value)

    @staticmethod
    def _parse_tag_item(type_, value):
        if hasattr(type_, 'parse'):
            parse_func = type_.parse
        else:
            parse_func = type_
        if hasattr(value, '__iter__'):
            return parse_func(unicode(value[0]))
        elif not value:
            return value
        else:
            return parse_func(unicode(value))        

