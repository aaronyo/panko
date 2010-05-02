class Entity():
    def __eq__( self, other ):
        return self.sameId( other )

    def __neq__( self, other ):
        return not __eq__( self, other )

    def sameId( self, other ):
        return self.id == other.id
    
    @property
    def id( self ):
        raise NotImplementedError()
