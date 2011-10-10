class Bytes(str):
    # Marker class to distinguish raw bytes for ascii strings
    # Some operations appropriate for basestring but not Bytes,
    # like joining multivalued tags on "/".  Also, Bytes string-escapes
    # data when requested as a str.
    
    @staticmethod
    def parse(value):
        return Bytes(value)
        
    def __unicode__(self):
        return unicode(self.__str__())
        
    def __str__(self):
        return self.encode('string-escape')
        
    def __repr__(self):
        return "Bytes('%s')" % self.__str__()