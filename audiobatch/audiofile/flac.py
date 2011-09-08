from mutagen import flac

EXTENSIONS = ['flac']

class FLACTranslator( object ):
    kind = 'FLAC'
    mutagen_class = flac.FLAC

    def tag_mapping(self):
        return {
            "artists"            : "artist",
            "composers"          : "composer",
            "genres"             : "genre",
            "isrc"               : "isrc",
            "title"              : "title",
            "track_number"       : "tracknumber",
            "track_total"        : "tracktotal",
            "disc_number"        : "discnumber",
            "disc_total"         : "disctotal",
            "album.title"        : "album",
            "album.artists"      : "albumartist",
            "album.release_date" : "date"
        }

    def has_cover_art(self, flac_obj):
        # FIXME: implement
        return False