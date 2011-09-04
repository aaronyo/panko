import os.path
from .time_stamp import TimeStamp
import collections
from . import image

class ImageSet(collections.MutableMapping):
    image_spec = { \
        "cover": image.ImageRef
    }
    
    def __init__(self):
        self._images = {} 

    def __len__( self ):
        return len(self._images)

    def __contains__( self, key ):
        return key in self._images

    def __iter__( self ):
        return iter(self._images)

    def __getitem__(self, key):
        return self._images[key]

    def __delitem__(self, key):
        del sel._images[key]

    def __setitem__(self, key, value):
        if key not in image_spec:
            raise Exception("an ImageSet does not have key '%s'" % key)
        self._images[key] = value


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
        flat_tags = {}
        for k, v in tags:
            if isinstance( v, track.TagSet ):
                for sub_k, sub_v in v:
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
                return parse_func(value[0])
            else:
                return parse_func(value)


class AlbumTagSet(TagSet):
    tag_spec = { \
        "artists": [unicode],
        "composers": [unicode],
        "title": unicode,
        "release_date": TimeStamp,
        "isrc": str,
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


class Track(object):
    def __init__( self, mod_time, path, tags=None, raw_tags=None, images=None ):
        self.path = path
        self.tags = tags or TrackTagSet()
        self.raw_tags = raw_tags
        self.images = images or ImageSet()

    @property
    def extension( self ):
        _, ext = os.path.splitext( self.path )
        return ext

    @property
    def id( self ):
        return self.path

    def __eq__( self, other ):
        return ( self.id == other.id )

    def __ne__( self, other ):
        return not self.__eq__( other )
