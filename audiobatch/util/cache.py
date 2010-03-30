import UserDict
import collections

class LRUCache( object, UserDict.DictMixin ):
    """
    Credit:
    Python Cookbook, 2d ed., by Alex Matelli, Anna Martelli Ravenscroft,
    and David Ascher (O'Reilly Media, 2005) 0-596-00797-3

    A mapping that remembers the most recently accessed 'num_entries' items.

    Depends on a dict and a deque, so performance of most operations is
    O(1) or amortized O(1).  The exception is del, which will be O(n) for
    removing the item from the deque.
    """
    def __init__( self, num_entries, dct=() ):
        self._num_entries = num_entries
        self._dct = dict( dct )
        self._dque = collections.deque()

    def __repr__( self ):
        return '%r(%r,%r)' % (
            self.__class__.__name__, self._num_entries, self._dct)
        
    def copy( self ):
        return self.__class__( self._num_entries, self._dct )

    def keys( self ):
        return list( self._dque)
        
    def __getitem__( self, key ):
        if key in self._dct:
            self._dque.remove( key )
        else:
            raise KeyError
        self._dque.append( key )
        return self._dct[ key ]

    def __setitem__( self, key, value ):
        dct = self._dct
        dque = self._dque
        if key in dct:
            dque.remove( key )
        dct[ key ] = value
        dque.append( key )
        if len( dque ) > self._num_entries:
            del dct[ dque.popleft() ]

    def __delitem__( self, key ):
        self._dct.pop( key )
        _remove_from_deque( self._dque, key )

    def _remove_from_deque( dque, val_ ):
        for idx, val in enumerate( dque ):
            if val == val_:
                del dque[ idx ]
            return
        raise ValueError, '%r not in %r' % (val_, dque)

    # a method explicitly defined only as an optimization
    def __contains__( self, item ):
        return item in self._dct

    has_key = __contains__
