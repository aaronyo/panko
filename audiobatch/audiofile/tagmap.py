from collections import namedtuple
import re
from ..model.timeutil import FlexDateTime
import yaml

DEFAULT_MAP=\
r"""
album_titles:
    type: unicode[]
    mp4: \xa9alb
    mp3: TALB   
    flac: albumtitle

album_artists:
    type: unicode[]
    mp4: aART
    mp3: TPE2
    flac: albumartist

album_release_date:
    type: FlexDateTime
    mp4: \xa9day
    mp3: TDRC
    flac: date

artists:
    type: unicode[]
    mp4: \xa9alb
    mp3: TPE1
    flac: artist

composers:
    type: unicode[]
    mp4: \xa9wrt
    mp3: TCOM
    flac: composer

titles:
    type: unicode[]
    mp4: \xa9nam
    mp3: TIT2
    flac: title

track_number:
    type: int
    mp4: trkn[0]
    mp3: TRCK[0]
    flac: tracknumber
    
track_total:
    type: int
    mp4: trkn[1]
    mp3: TRCK[1]
    flac: [tracktotal, totaltracks]

disc_number:
    type: int
    mp4: disk[0]
    mp3: TPOS[0]
    flac: discnumber

disc_total:
    type: int
    mp4: disk[1]
    mp3: TPOS[1]
    flac: [disctotal, totaldiscs]

genres:
    type: unicode[]
    mp4: \xa9gen
    mp3: TCON
    flac: genre
"""

def load(data=DEFAULT_MAP):
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

class Location(namedtuple("Location", "name, part")):
    _matcher = re.compile("(?P<name>\w*)\[(?P<part>[0-9]+)\]")
    
    @staticmethod
    def parse(rep):
        m = Location._matcher.match(rep)
        if m: return Location( m.group('name'), int(m.group('part')) )
        else: return Location(rep, part=None)

    def __str__(self):
        if self.part != None:
            return "%s[%i]" % (self.name, self.part)
        else:
            return self.name