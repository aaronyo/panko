from mutagen import mp3, id3
import logging
import StringIO
import shutil

from audiobatch.persistence.audiofile import AudioFile
from audiobatch.model import audiostream, image, track, album, format

_LOGGER = logging.getLogger()

_COMMON_TO_ID3 = {
    "artists"            : id3.TPE1,
    "composers"          : id3.TCOM,
    "genres"             : id3.TCON,
    "isrc"               : id3.TSRC,
    "title"              : id3.TIT2,
    "track_number"       : None, # requires custom handling
    "track_total"        : None, # requires custom handling
    "disc_number"        : None, # requires custom handling
    "disc_total"         : None, # requires custom handling
    "album.title"        : id3.TALB,
    "album.artists"      : id3.TPE2,
    "album.release_date" : id3.TDRC
}

_ID3_TO_COMMON = dict( (v.__name__ if v else None, k) 
                       for k, v in _COMMON_TO_ID3.iteritems() )

_ID3_PIC_CODES = {
    image.SUBJECT__ALBUM_COVER : 3
}

EXTENSIONS = ["mp3"]

def _encode_pos_str( part, total ):
    if part == None and total == None:
        return None
    else:
        part = str( part ) if part != None else "" 
        total =  "/" + str( total ) if total != None else ""
        return u"%s%s" % ( part, total )
    
def _encode_TPOS_frame( disc_number, disc_total ):
    frame_text = _encode_pos_str( disc_number, disc_total )
    return id3.TPOS( encoding=3, text=frame_text ) if frame_text else None


def _encode_TRCK_frame( track_number, track_total ):
    frame_text = _encode_pos_str( track_number, track_total )
    return id3.TRCK( encoding=3, text=frame_text ) if frame_text else None

def _blank_safe_int( str ):
    return int( str ) if str != '' else None

def _decode_TRCK_frame( frame ):
    vals = frame.text[0].split("/")
    if len(vals) == 1:
        return _blank_safe_int( vals[0] ), None
    else:
        return _blank_safe_int( vals[0] ), _blank_safe_int( vals[1] )

def _decode_TPOS_frame( frame ):
    vals = frame.text[0].split("/")
    if len(vals) == 1:
        return _blank_safe_int( vals[0] ), None
    else:
        return _blank_safe_int( vals[0] ), _blank_safe_int( vals[1] )


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read( 128 )
    match_score = mp3.MP3.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class MP3File( AudioFile ):
    def __init__( self, path ):
        self._mp3_obj = mp3.MP3( path )
        AudioFile.__init__( self, path, self._mp3_obj )

    def get_audio_stream( self ):
        # Mutagen does not provide bitrate for FLAC
        # FIXME: Return 'None' and force client to handle?
        if self._updated_audio_stream == None:
            return audiostream.AudioStream( self._mp3_obj.info.bitrate,
                                            format.MP3_STREAM,
                                            self.path )
        else:
            return self._updated_audio_stream

    def clear_all( self ):
        self._mp3_obj.delete()
        
    def _update_album_info( self, album_info ):
        if self._mp3_obj.tags == None:
            self._mp3_obj.add_tags()

        self._add_images( album_info.images )
        for field_name, value in album_info.items():
            if field_name == "images":
                continue # handled in _add_images call above
            if field_name == "release_date":
                value = str( value )
            lookup_name = "album." + field_name
            if lookup_name in _COMMON_TO_ID3:
                id3_frame_class = _COMMON_TO_ID3[ lookup_name ]
                frame = id3_frame_class( encoding=3, text=value )
                self._mp3_obj.tags.add( frame )
            else: 
                _LOGGER.error( "Can't write '%s' - ID3 mapping not found"
                               % lookup_name )

    def _update_track_info( self, track_info ):
        if self._mp3_obj.tags == None:
            self._mp3_obj.add_tags()

        # id3 combines the number and total into a single field of
        # format: "number/total"
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        for field_name, value in track_info.items():
            if field_name in _COMMON_TO_ID3:
                if field_name == "track_number":
                    track_number = value
                elif field_name == "track_total":
                    track_total = value
                elif field_name == "disc_number":
                    disc_number = value
                elif field_name == "disc_total":
                    disc_total = value
                else:
                    id3_frame_class = _COMMON_TO_ID3[ field_name ]
                    frame = id3_frame_class( encoding=3, text=value )
                    self._mp3_obj.tags.add( frame )
            else: 
                _LOGGER.error( "Can't write '%s' - ID3 mapping not found"
                               % field_name )
            
        tpos_frame = _encode_TPOS_frame( disc_number, disc_total )
        if tpos_frame != None:
            self._mp3_obj.tags.add( tpos_frame )

        trck_frame = _encode_TRCK_frame( track_number, track_total )
        if trck_frame != None:
            self._mp3_obj.tags.add( trck_frame )


    def _get_info( self ):
        def _update_field( info, field_name, mp3_value ):
            if info.is_multi_value( field_name ):
                info[ field_name ] = [ unicode(x) for x in mp3_value.text ]
            else:
                    # important to call unicode() as some values are
                    # not actually strings -- only string like -- and lack
                    # important methods like the default string cmp()
                info[ field_name ] = unicode( mp3_value.text[0] )

        album_info = album.AlbumInfo()
        track_info = track.TrackInfo()

        mp3_obj = self._mp3_obj

        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        for tag_name, value in mp3_obj.items():
            if tag_name in _ID3_TO_COMMON:
                field_name = _ID3_TO_COMMON [ tag_name ]
                if field_name.startswith("album."):
                    field_name = field_name[6:]
                    _update_field( album_info, field_name, value )
                else:
                    _update_field( track_info, field_name, value )
            # id3 combines the number and total into a single field of
            # format: "number/total"
            elif tag_name == id3.TRCK.__name__:
                track_number, track_total = _decode_TRCK_frame( value )
            elif tag_name == id3.TPOS.__name__:
                disc_number, disc_total = _decode_TPOS_frame( value )
            else:
                _LOGGER.debug( "Can't read MP3 tag "
                               + "'%s' - common mapping not found"
                               % tag_name )

        track_info[ "track_number"] = track_number
        track_info[ "track_total" ] = track_total
        track_info[ "disc_number" ] = disc_number
        track_info[ "disc_total" ] = disc_total 

        return album_info, track_info

    def _add_images( self, images ):
        for subject, img in images.items():
            if _ID3_PIC_CODES.has_key( subject ):
                id3_pic_code = _ID3_PIC_CODES[ subject ]
            else:
                _LOGGER.warn( ( "ID3 mapping for image subject '%s' not " +
                                "found.  Will not be written to mp3: %s" )
                              % (subject, self.path) )
                continue
 
            apicFrame = id3.APIC( encoding = 3,
                                  mime = 'image/jpeg',
                                  type = id3_pic_code,
                                  desc = u'%s' % subject,
                                  data = img.get_bytes() )
            self._mp3_obj.tags.add( apicFrame )
        

    def __repr__( self ):
        return self._mp3_obj.__repr__()



