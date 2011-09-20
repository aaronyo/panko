from collections import namedtuple
import re
from ..model.timeutil import FlexDateTime
from . import tagmap_config
import yaml


def load(data=tagmap_config.DEFAULT_MAP):
    return TagMap(data)

class TagMap(object):
    def __init__(self, data):
        self.tag_types = {}
        self.locations = {'mp3':{}, 'mp4':{}, 'flac':{}}
        yaml_obj = yaml.load(data)
        for tag_name, specs in yaml_obj.items():
            self.tag_types[tag_name] = TagType.parse( specs.pop('type') )
            for format, locs in specs.items():
                tag_locs = []
                if not hasattr(locs, '__iter__'):
                    locs = [locs]
                for loc in locs:
                    tag_locs.append( Location.parse(loc) )
                self.locations[format][tag_name] = tag_locs

class TagType(namedtuple("TagType", "type_, is_multival")):
    @staticmethod
    def parse(rep):
        if rep.endswith("[]"):
            rep = rep[:-2]
            is_multival = True
        else:
            is_multival = False
        type_ = __builtins__.get(rep, None)
        if not type_:
            if rep == 'FlexDateTime':
                type_ = FlexDateTime
        return TagType(type_, is_multival )

    def __str__(self):
        if self.is_multival:
            return "%s[]" % self.type_.__name__
        else:
            return self.type_.__name__

class Location(object):
    _matcher = re.compile("(?P<key>\w*)\[(?P<part>[0-9]+)\]")
    
    def __init__(self, key, part=None):
        self.key, self.part = key, part
    
    @staticmethod
    def parse(rep):
        m = Location._matcher.match(rep)
        if m:
            key, part = m.group('key'), int(m.group('part'))
        else:
            key, part = rep, None
        # we want the plain escaped ascii for keys to be compatible
        # with mutagen, so use repr and ditch the quotes
        return Location(key, part)

    def __str__(self):
        if self.part != None:
            return "%s[%i]" % (self.key, self.part)
        else:
            return self.key