from types import ListType, IntType, DictType

from audiobatch.model import track, _info


class Album( object ):
    def __init__( self ):
        self._tracks = []

    def num_tracks( self ):
        return len( self._tracks )

    def add_track( self, track ):
        self._tracks.append( track )

    def get_tracks( self ):
        return self._tracks


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
