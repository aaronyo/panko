class FileIO( object ):
    """
    """
    default_cover_key = None
    
    def __init__(self, mtg_file):
        self.mtg_file = mtg_file

    def save(self):
        self.mtg_file.save()
        
    def clear_tags(self):
        # We don't want to delete the cover art
        map(self.mtg_file.__delitem__, self.keys())

    def keys(self):
        return self.mtg_file.keys()
                
    def set_tag(self, location, value):
        raise NotImplementedError

    def get_tag(self, location):
        raise NotImplementedError
    
    def get_raw(self, key):
        return self.mtg_file.get(key, None)

    def set_cover_art(self, bytes, mime_type):
        raise NotImplementedError

    def get_cover_art(self):
        raise NotImplementedError
    
    def cover_art_key(self):
        raise NotImplementedError
