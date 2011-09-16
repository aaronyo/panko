class MutagenWrapper( object ):
    """
    """
    
    def __init__(self, mtg_file):
        self.mtg_file = mtg_file

    def save(self):
        self.mtg_file.save()
        
    def keys(self):
        return self.mtg_file.keys()
                
    def set_tag(self, location_spec, value):
        return NotImplementedError

    def get_tag(self, location_spec):
        return NotImplementedError

    def embed_cover_art(self, img):
        return NotImplementedError

    def extract_cover_art(self):
        return NotImplementedError

    def has_cover_art(self):
        return NotImplementedError
