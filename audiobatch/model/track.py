import os.path
from .timeutil import LenientDateTime
import collections

class TagSet(collections.MutableMapping):
    # A dictionary with a couple added features:
    #   1. Parse and validate keys and values against a spec
    #   2. Provided a flattened view with "dot" notation for nested dicts/TagSets
    
    def __init__(self, tags=None):
        self._tags = dict(tags or {})

    def __len__( self ):
        return len(self._tags)

    def __contains__( self, key ):
        return key in self._tags

    def __iter__( self ):
        return iter(self._tags)

    def __getitem__(self, key):
        return self._tags[key]

    def __setitem__(self, key, value):
        self._tags[key] = value
        
    def __delitem__(self, key):
        del self._tags[key]
        
    def __repr__(self):
        return '%s( %s ) ' % ( self.__class__.__name__, repr(self._tags) )

    def parse(self, dotted_key, value):
            key, sub_key = (dotted_key.split('.') + [None])[:2]
            if sub_key:
                if key not in self._tags:
                    self._tags[key] = self.tag_spec[key]()
                sub_spec = self.tag_spec[key].tag_spec[sub_key]
                self._tags[key][sub_key] = \
                    TagSet._apply_type_spec(sub_spec, value)
            else:
                self._tags[key] = \
                    TagSet._apply_type_spec(self.tag_spec[key], value)

    def flat(self):
        return self.flatten(self._tags)

    @staticmethod
    def flatten(tags):
        flat_tags = {}
        for k, v in tags.items():
            if isinstance( v, collections.Mapping ):
                for sub_k, sub_v in v.items():
                    flat_tags[k+'.'+sub_k] = sub_v
            else:
                flat_tags[k] = v
        return flat_tags 

    @staticmethod
    def _apply_type_spec(type_spec, value):
        if type(type_spec) == list:
            return [TagSet._apply_type_spec(type_spec[0], v) for v in value]
        else:
            if hasattr(type_spec, 'parse'):
                parse_func = type_spec.parse
            else:
                parse_func = type_spec
            if hasattr(value, '__getitem__') and not isinstance( value,
                                                                 basestring ):
                return parse_func(unicode(value[0]))
            else:
                return parse_func(unicode(value))


class AlbumTagSet(TagSet):
    tag_spec = { \
        "artists": [unicode],
        "composers": [unicode],
        "title": unicode,
        "release_date": LenientDateTime
    }

class TrackTagSet(TagSet):
    tag_spec = { \
        "artists": [unicode],
        "title": unicode,
        "track_number": int,
        "track_total": int,
        "disc_number": int,
        "disc_total": int,
        "composers": [unicode],
        "genres": [unicode],
        "isrc": str,
        "album": AlbumTagSet
    }        


class PathImageRef( object ):
    def __init__(self, path):
        self.path = path
        self.kind = 'path'


class Track(object):
    def __init__( self, path, mod_time, translator, tags=None, raw_tags=None,
                  folder_cover_art=None, embedded_cover_art=False ):
        self.path = path
        self.mod_time = mod_time
        self.translator = translator
        self.tags = tags or TrackTagSet()
        self.raw_tags = raw_tags
        self.has_embedded_cover_art = embedded_cover_art
        self.folder_cover_art = folder_cover_art
        
    @property
    def extension( self ):
        _, ext = os.path.splitext( self.path )
        return ext

    @property
    def id( self ):
        return self.path
        
    @property
    def folder_cover_art_path( self ):
        if self.folder_cover_art:
            return os.path.join( os.path.dirname(self.path),
                                 self.folder_cover_art)
    
    @property
    def has_folder_cover_art( self ):
        return bool(self.folder_cover_art)
    
    def pretty( self ):
        def pretty_value(value):
            if hasattr(value, '__iter__'):
                return u", ".join([pretty_value(v) for v in value])
            elif isinstance(value, basestring):
                return u'"%s"' % value
            else:
                return unicode(value)
        
        TagRow = collections.namedtuple('TagRow', "common raw value")
        raw_tags = dict(self.raw_tags)
        tags = sorted(self.tags.flat().items())
        rows = []
        mapping = self.translator.tag_mapping()
        for tag, value in tags:
            raw_tag = mapping[tag]
            if hasattr(raw_tag, '__iter__'):
                if isinstance(raw_tag[1], basestring):
                    for r in raw_tag:
                        if r in raw_tags:
                            raw_tag = r; break
                else:
                    raw_tag = raw_tag[0]
            rows.append( TagRow(tag, raw_tag, pretty_value(value)) )
            try:
                raw_tags.pop(raw_tag)
            except KeyError:
                pass #Tag must be a multi-value tag -- can't pop twice
            
        raw_tags = sorted(raw_tags.items())
        for raw_tag, value in raw_tags:
            rows.append( TagRow('(unrecognized)', raw_tag, pretty_value(value)) )
        
        pretty_str = u""
        
        lengths = [(len(c), len(r), len(v)) for c, r, v in rows]
        col_lengths = zip(*lengths)
        pad = [ max(l)+1 for l in col_lengths ]

        for row in rows:
            pretty_str += u"%-*s: %-*s: %s\n" \
                % (pad[0], row.common, pad[1], unicode(row.raw, 'latin-1'), row.value)
        
        return pretty_str
        
    def __repr__( self ):
        representation = \
"""%(path)s
%(mod_time)s
%(tags)s
%(raw_tags)s
%(has_embedded_cover_art)s
%(folder_cover_art)s""" % self.__dict__

        
        return representation

    def __eq__( self, other ):
        return ( self.id == other.id )

    def __ne__( self, other ):
        return not self.__eq__( other )
