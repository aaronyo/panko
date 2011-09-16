from collections import namedtuple
import re
from ..model.timeutil import FlexDateTime
import yaml

DEFAULT_TRANSLATION=\
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
"""

def load(data=DEFAULT_TRANSLATION):
    return TranslationSpec(data)

class TranslationSpec(object):
    def __init__(self, data):
        self.type_specs = {}
        self.location_specs = {'mp3':{}, 'mp4':{}, 'flac':{}}
        yaml_obj = yaml.load(data)
        for tag_name, specs in yaml_obj.items():
            self.type_specs[tag_name] = TypeSpec.parse( specs.pop('type') )
            for format, locations in specs.items():
                loc_specs = []
                if not hasattr(locations, '__iter__'):
                    locations = [locations]
                for loc in locations:
                    loc_specs.append( LocationSpec.parse(loc) )
                self.location_specs[format][tag_name] = loc_specs

class TypeSpec(namedtuple("TypeSpec", "type_, is_multival")):
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
        return TypeSpec(type_, is_multival )

    def __str__(self):
        if self.is_multival:
            return "%s[]" % self.type_.__name__
        else:
            return self.type_.__name__
                          
class LocationSpec(namedtuple("LocationSpec", "raw_name, part")):
    _matcher = re.compile("(?P<raw_name>\w*)\[(?P<part>[0-9]+)\]")
    
    @staticmethod
    def parse(rep):
        m = LocationSpec._matcher.match(rep)
        if m: return LocationSpec( m.group('raw_name'), int(m.group('part')) )
        else: return LocationSpec(rep, part=None)

    def __str__(self):
        if self.part != None:
            return "%s[%i]" % (self.raw_name, self.ref)
        else:
            return self.name
            

            



#    @staticmethod
#    def _write_tags( self, tags, mtg_file ):
#        flat_tags = model.track.TrackTagSet.flatten(tags)
#        for common_tag, value in flat_tags.items():
#            if common_tag.endswith('date'):
#                # mutagen can't handle our custom 'LenientDateTime' class
#                value = str(value)
#            mapping = self._mapping[common_tag]
#            if isinstance(mapping, basestring):
#                self._mutagen_obj[mapping] = value
#            else:
#                mapping[1](value, self._mutagen_obj)
#        
#    def has_cover_art( self ):
#        return self.translator.has_cover_art(self._mutagen_obj)
#
#    def embed_cover_art( self, img ):
#        self.translator.embed_cover_art( self._mutagen_obj,
#                                         img.bytes, img.full_mime_type() )
#
#    def extract_cover_art( self ):
#        return Image( * self.translator.extract_cover_art(self._mutagen_obj) )
#
#    def clear_tags( self ):
#        self._mutagen_obj.delete()
#
#    def raw_tags( self ):
#        return dict(self._mutagen_obj)
#
#    def save( self ):
#            self._mutagen_obj.save()
#
#    def _copy_tags_to( self, target_path ):
#        """ Copy tags to a file of the same format as this AudioFile. """
#        mutagen_class = self._mutagen_obj.__class__
#        mutagen_obj = mutagen_class( target_path )
#        mutagen_obj.update( self._mutagen_obj.items() )
#        mutagen_obj.save()
#
#    @staticmethod
#    def _unicode_all( val ):
#        if not isinstance(val, basestring) and has_attr(val, '__iter__'):
#            return [ unicode(x) for x in val ]
#        else:
#            return unicode( val )
#