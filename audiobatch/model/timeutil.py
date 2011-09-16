import datetime

class FlexDateTime( object ):
    @staticmethod
    def parse( text, allow_invalids = True):
        year, month, day, hour, min, sec = [None] * 6
        # Replace missing vals with None
        if " " in text:
            date, time = ( tuple(text.split(" ")) + (None, None) )[:2]
        elif "T" in text:
            date, time = ( tuple(text.split("T")) + (None, None) )[:2] 
        else:
            date = text
            time = None
            
        if date != None:
            year, month, day = \
                (tuple(date.split("-")) + (None, None, None) )[:3]
        if time != None:
            hour, min, sec = \
                ( tuple(time.split("-")) + (None, None, None) )[:3]
        
        return FlexDateTime( *( int(x) if x else None for x
                             in (year, month, day)), #, hour, min, sec) ),
                           allow_invalids = allow_invalids )

    _formats = ['%04i'] + ['%02i'] * 5
    _seps = ['-', '-', ' ', ':', ':', 'x']

    def date(self):
        return FlexDateTime(self.year, self.month, self.day)

    def __str__(self):
        vals = [ self.year, self.month, self.day,
                 self.hour, self.min, self.sec ]
        seq = []
        for val, format, sep in zip(vals, self._formats, self._seps):
            if not val: break
            seq.append( format % val + sep )

        return ''.join(seq)[:-1]
        

    def __repr__(self):
        vals = [ self.year, self.month, self.day,
                 self.hour, self.min, self.sec ]
        seq = []
        for val in vals:
            if not val: break
            seq.append(repr(val))
        params = ', '.join(seq)
        return "%s( %s )" % (self.__class__.__name__, params)

    def __init__( self,
                  year,
                  month = None,
                  day = None,
                  hour = None,
                  min = None,
                  sec = None ,
                  allow_invalids = True):

        '''
        Interpretation stops at the first None or invalid value.
        
        If lenient is set to true, an error is not raised for an invalid,
        .e.g. out of range, value.
        '''
        self.allow_invalids = allow_invalids
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
            if self.allow_invalids:
                return False
            else:
                raise ve
        return True

    def  _validate_range( self, val, min, max, name ):
        if min <= val <= max:
            return True
        elif self.allow_invalids:
            return False
        else:
            raise ValueError( "%s must be in range %d..%d" % (name, min, max) )

    def __eq__( self, other ):
        return str( self ) == str( other )