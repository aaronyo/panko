from mutagen import mp3, id3
import logging
import StringIO

_LOGGER = logging.getLogger()

_COMMON_TO_ID3 = {
    "album_title"  : id3.TALB,
    "album_artist" : id3.TPE2,
    "artist"       : id3.TPE1,
    "composer"     : id3.TCOM,
    "date"         : id3.TDRC,
    "disc_number"  : None,  # requires custom handling
    "disc_total"   : None,  # requires custom handling
    "genre"        : id3.TCON,
    "isrc"         : id3.TSRC,
    "title"        : id3.TIT2,
    "track_number" : None, # requires custom handling
    "track_total"  : None, # requires custom handling
}

_IMAGE_ENCODING_TO_MIME_TYPE = {
    "jpeg" : "image/jpeg",
    "png"  : "image/png"
}

_IMAGE_SUBJECT_TO_ID3_CODE = {
    "album_cover" : 3
}


def _make_tpos_frame( disc_number, disc_total ):
    if disc_number == None:
        return None
    elif disc_total == None:
        frame_text = u"%d" % disc_number
    else:
        frame_text = u"%d/%d" % ( disc_number, disc_total )

    return id3.TPOS( encoding=3, text=frame_text )


def _make_trck_frame( track_number, track_total ):
    if track_number == None:
        return None
    elif track_total == None:
        frame_text = u"%d" % track_number
    else:
        frame_text = u"%d/%d" % ( track_number, track_total )

    return id3.TRCK( encoding=3, text=frame_text )


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read( 128 )
    match_score = mp3.MP3.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class Mp3File:
    def __init__( self, path ):
        self.path = path
        self._mp3_obj = mp3.MP3( path )

    @property
    def bitrate(self):
        return self._mp3_obj.info.bitrate

    def clear_all( self ):
        self._mp3_obj.delete()
        
    def add_tags( self, tags ):
        # id3 combines the number and total into a single field of
        # format: "number/total"
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        for tag_name, value in tags.items():

            if tag_name == "disc_number":
                disc_number = value
            elif tag_name == "disc_total":
                disc_total = value
            elif tag_name == "track_number":
                track_number = value
            elif tag_name == "track_total":
                track_total = value

            else:
                try:
                    frame_class = _COMMON_TO_ID3[ tag_name ]
                except KeyError:
                    _LOGGER.warn( ("Id3 mapping for common tag '%s' not " +
                                   "found. Will not be written to mp3: %s") \
                                      % (tag_name, self.path) )
                    continue

                frame_obj = frame_class(encoding=3, text=value)
                self._mp3_obj[ frame_class.__name__ ] = frame_obj

        tpos_frame = _make_tpos_frame(disc_number, disc_total)
        if tpos_frame != None:
            self._mp3_obj[ tpos_frame.__class__.__name__ ] = tpos_frame
            
        trck_frame = _make_trck_frame(track_number, track_total)
        if trck_frame != None:
            self._mp3_obj[ trck_frame.__class__.__name__ ] = trck_frame

    def add_images(self, image_dict, encoding ):
        mime_type = _IMAGE_ENCODING_TO_MIME_TYPE[encoding]
        for subject, image in image_dict.items():
            if _IMAGE_SUBJECT_TO_ID3_CODE.has_key( subject ):
                id3_pic_code = _IMAGE_SUBJECT_TO_ID3_CODE[ subject ]
            else:
                _LOGGER.warn( ("Id3 mapping for image subject '%s' not " +
                               "found. Will not be written to mp3: %s") \
                                  % (subject, self.path) )
                continue

            # Image is a PIL Image object.  Get the binary data in encoding of
            # our choice.
            # FIXME: image should already be an encoded byte stream so that
            # this work doesn't have to be repeated in each specific container
            # type
            buf = StringIO.StringIO()
            image.save( buf, format=encoding )
            image_data = buf.getvalue()
            buf.close()

            apic_frame = id3.APIC( encoding = 3,
                                  mime = mime_type,
                                  type = id3_pic_code,
                                  desc = u'AlbumCover',
                                  data = image_data )
            self._mp3_obj.tags.add( apic_frame )
            

    def save( self ):
        self._mp3_obj.save()

