import bisect
from types import ListType, IntType, DictType

from audiobatch.model import track, _info, entity


class Album( object, entity.Entity ):

    def num_tracks( self ):
        raise NotImplementedError()

    def add_track( self, track ):
        raise NotImplementedError()

    def get_tracks( self ):
        raise NotImplementedError()

    def set_album_info( self, album_info ):
        raise NotImplementedError()

    def get_album_info( self ):
        raise NotImplementedError()
        
class DTOAlbum( Album ):
    def __init__( self ):
        self._tracks = []
        # set the sort to enable use of bisect when adding tracks
        self._tracks.sort( key = lambda t: t.get_track_info().track_number )

    def num_tracks( self ):
        return len( self._tracks )

    def add_track( self, track ):
        bisect.insort_right( self._tracks, track )

    def get_tracks( self ):
        return self._tracks

    def set_album_info( self, album_info ):
        self._album_info = album_info

    def get_album_info( self ):
        return self._album_info

    @property
    def id( self ):
        return ' '.join([ t.id() for t in self._tracks ])


class AlbumInfo( _info.Info ):
    def __init__( self, fields_dict = None ):
        _info.Info.__init__( self )
        self._add_field( "artists", ListType )
        self._add_field( "composers", ListType )
        self._add_field( "title" )
        self._add_field( "release_date", _info.TimeStamp )
        self._add_field( "isrc" )
        # valid keys are described in the 'model.image' module
        self.images = {}
        self._add_field( "images", DictType )
        if fields_dict != None: self.update( fields_dict )

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None
