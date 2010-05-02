from collections import namedtuple
from types import ListType, DictType, IntType
import UserDict
import datetime

_Field = namedtuple( "Field", "name, mandatory_type, value" )

class TimeStamp( object ):
    @staticmethod
    def parse( text, is_lenient = False ):
        year, month, day, hour, min, sec = [None] * 6
        # Replace missing vals with None
        date, time = ( tuple(text.split(" ")) + (None, None) )[:2]
        if date != None:
            year, month, day = \
                (tuple(date.split("-")) + (None, None, None) )[:3]
        if time != None:
            hour, min, sec = \
                ( tuple(time.split("-")) + (None, None, None) )[:3]
        
        return TimeStamp( *( int(x) if x else None for x
                             in (year, month, day, hour, min, sec) ),
                           is_lenient = is_lenient )

    _formats = ['%04d'] + ['%02d'] * 5
    _seps = ['-', '-', ' ', ':', ':', 'x']
    def __str__( self ):
        vals = [ self.year, self.month, self.day,
                 self.hour, self.min, self.sec ]
        seq = []
        for val, format, sep in zip(vals, self._formats, self._seps):
            if not val: break
            seq.append( format % val + sep )
        
        return ''.join(seq)[:-1]

    def __init__( self,
                  year,
                  month = None,
                  day = None,
                  hour = None,
                  min = None,
                  sec = None ,
                  is_lenient = False):

        '''
        Interpretation stops at the first None or invalid value.
        
        If lenient is set to true, an error is not raised for an invalid,
        .e.g. out of range, value.
        '''

        self.is_lenient = is_lenient
        self.year, self.month, self.day, self.hour, self.min, self.sec =\
            [None] * 6

        if not self._validate_range( year, 1, 9999, "year" ) : return
        self.year = year

        if not month \
        or not self._validate_range( month, 1, 12, "month" ): return
        self.month = month

        if not day \
        or not self._is_valid_day( day ): return
        self.day = day

        if not hour \
        or not self._validate_range( hour, 0, 23, "hour" ): return
        self.hour = hour

        if not min \
        or not self._validate_range( min, 0, 59, "min" ): return
        self.min = min

        if not sec \
        or not self._validate_range( sec, 0, 59, "sec" ): return
        self.sec = sec
        
    def _is_valid_day( self, day ):
        ''' Assumes month and year are already validated '''
        if day == None:
            return False
        try:
            datetime.date( self.year, self.month, day )
        except ValueError as ve:
            if self.is_lenient:
                return False
            else:
                raise ve
        return True

    def  _validate_range( self, val, min, max, name ):
        if min <= val <= max:
            return True
        elif self.is_lenient:
            return False
        else:
            raise ValueError( "%s must be in range %d..%d" % (name, min, max) )

    def __eq__( self, other ):
        return str( self ) == str( other )


class Info( object, UserDict.DictMixin ):

    def __init__( self ):
        self._fields = {}

    def __setattr__( self, name, val ):
        if name == "_fields":
            object.__setattr__( self, name, val )
            return

        if name in self._fields.keys():
            old_field = self._fields[ name ]
            self._fields[ name ] = old_field._replace( value = val )
        else:
            object.__setattr__( self, name, val )

    def __deepcopy__( self, memo ):
        return self.__class__( self )

    def __getattr__( self, name ):
        # to make pickling work
        if ( name == "__slots__" ):
            raise AttributeError

        return self._fields[ name ].value

    def keys( self ):
        field_keys = []
        for k, v in self._fields.items():
            if v.value != None:
                field_keys.append( k )
        return field_keys

    def __getitem__( self, key ):
        """ The dictionary accessors provide string based access to a
        tracks information.  This is a convenience for configuring
        access with strings, say in a config file or dictionary, and
        and restricting access to only those attributes that are
        tags.""" 
        info_obj, specific_key = self._which( key )
        val = info_obj._fields[ specific_key ].value
        if val == None:
            raise KeyError(key)
        else:
            return val

    def __setitem__( self, key, val ):
        info_obj, specific_key = self._which( key )
        old_field = info_obj._fields[ specific_key ]
        info_obj._fields[ specific_key ] = old_field._replace( value = val )

    def __getstate__( self ):
        return self.items()

    def __setstate__( self, items ):
        for k, v in items:
            self.__setitem__( k, v )

    def __eq__( self, other ):
        '''
        An equality operator that works with anything dict like.
        
        When comparing an info object to an actual built in dict, the comparison
        will work no matter what side of the '==' the objects are on.  This is
        due to some python magic that causes this __eq__ method to be used
        in either case.
        '''

        # FIXME -- what's the best way to do DictMixin == DictMixin?
        # this approach isn't great if items() doesn't guarantee dict()
        # constructor will work
        if callable( getattr( other, "items", None )  ):
            return dict( self ) == dict( other )
        else:
            return False

    def __ne__( self, other ):
        return not self.__eq__( other )

    def _add_field( self, name, mandatory_type = None ):
        self._fields[name] = _Field( name, mandatory_type, None)

    def _which( self, field_name ):
        return self, field_name

    def _assert_is_field( self, field_name ):
        if field_name not in self.__dict__:
            raise AttributeError, "'%s' not a track tag" % field_name

    def is_multi_value( self, key ):
        # FIXME should be staticly determinable
        info_obj, specific_key = self._which( key )
        field_type = info_obj._fields[ specific_key ].mandatory_type
        return ( field_type == ListType
                 or field_type == DictType )
    
    def is_int( self, key ):
        info_obj, specific_key = self._which( key )
        field_type = info_obj._fields[ specific_key ].mandatory_type
        return field_type == IntType

