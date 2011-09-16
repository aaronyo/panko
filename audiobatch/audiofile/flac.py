from mutagen import flac

EXTENSIONS = ['flac']

class FLACTranslator( object ):
    kind = 'FLAC'

    def _set_file_tag(self, format_key, value, mtg_file):
        mtg_file[format_key.name] = value
        
    def _get_file_tag(self, format_key, mtg_file):
        return mtg_file.get(format_key.name, None)

    def open_mtg_file(self, path):
        return flac.FLAC(path)

