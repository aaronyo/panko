import logging
import mutagen.flac

_LOGGER = logging.getLogger()

_FLAC_TO_COMMON = {
    "ALBUM"       : "album_title",
    "ALBUMARTIST" : "album_artist",
    "ARTIST"      : "artist",
    "COMPOSER"    : "composer",
    "DATE"        : "date",
    "DISCNUMBER"  : "disc_number",
    "DISCTOTAL"   : "disc_total",
    "GENRE"       : "genre",
    "ISRC"        : "isrc",
    "TITLE"       : "title",
    "TRACKNUMBER" : "track_number",
    "TRACKTOTAL"  : "track_total"
    }

_COMMON_TO_FLAC = dict( (value, key) 
                        for key, value 
                        in _FLAC_TO_COMMON.iteritems()
                        )


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read(128)
    match_score = mutagen.flac.FLAC.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class FlacFile():
    def __init__( self, path ):
        self._flac_obj = mutagen.flac.FLAC( path )
        self.path = path

    @property
    # Ignore warning that this could be a function.  This property is part
    # of the AudioFile duck type's interface.
    # pylint: disable-msg = R0201
    def bitrate(self):
        # Mutagen does not provide bitrate for FLAC
        # FIXME: Return 'None' and force client to handle?
        return 900000

    def get_tags( self ):
        common_tags = {}

        for flac_tag_name, value in self._flac_obj.items():
            try:
                common_tag_name = _FLAC_TO_COMMON[ flac_tag_name.upper() ]
            except KeyError:
                _LOGGER.warn("Common mapping for flac tag '%s' not found" \
                                 % flac_tag_name)
                continue

            if common_tag_name.endswith("total") \
                    or common_tag_name.endswith("number"):
                common_tags[common_tag_name] = int(value[0])
            else:
                unicode_values = [unicode(x) for x in value]
                common_tags[common_tag_name] = unicode_values

        return common_tags

    def add_tags( self, tags ):
        for tag_name, tag_value in tags.items():

            try:
                flac_tag_name =  _COMMON_TO_FLAC[tag_name]
            except KeyError:
                # FIXME: Need helper methods for code that is common across
                # file types.
                _LOGGER.warn( ("Flac mapping for common tag '%s' not found. " +
                               "Will not be written to flac: %s") \
                                     % (flac_tag_name, self.path) )
                continue

            self._flac_obj[ flac_tag_name ] = tag_value

    def save( self ):
        self._flac_obj.save()
