import types

class AlbumInfo( object ):
    def __init__( self ):
        self.artists = []
        self.composers = []
        self.title = None
        self.release_date = None
        self.isrc = None
        self.disc_total = None
        # valid keys are described in the 'model.image' module
        self.images = {}

    @property
    def primary_artist( self ):
        if len( self.artists ) > 0:
            return self.artists[0]
        else:
            return None
