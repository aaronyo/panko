from mutagen import mp3, id3
import logging
import StringIO
import shutil

from audiobatch.persistence.audiofile import AudioFile
from audiobatch.model import audiostream, image, track, format

_LOGGER = logging.getLogger()

_TRACK_INFO_TO_ID3 = {
    "artists"            : id3.TPE1,
    "composers"          : id3.TCOM,
    "release_date"       : id3.TDRC,
    "genre"              : id3.TCON,
    "isrc"               : id3.TSRC,
    "title"              : id3.TIT2,
    "track_number"       : None, # requires custom handling
    "track_total"        : None, # requires custom handling
    "disc_number"        : None, # requires custom handling
    "album.title"        : id3.TALB,
    "album.artists"      : id3.TPE2,
    "album.disc_total"   : None, # requires custom handling
}

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

    def set_audio_stream( self, audio_stream ):
        self._updated_audio_stream = audio_stream

    def clear_all( self ):
        self._mp3_obj.delete()
        
    def update_track_info( self, track_info ):
        # id3 combines the number and total into a single field of
        # format: "number/total"
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        if self._mp3_obj.tags == None:
            self._mp3_obj.add_tags()

        for tag_name, id3_frame_class in _TRACK_INFO_TO_ID3.items():
            if tag_name in track_info:
                tag_val = track_info[ tag_name ]
                if tag_name == "track_number":
                    track_number = tag_val
                elif tag_name == "track_total":
                    track_total = tag_val
                elif tag_name == "disc_number":
                    disc_number = tag_val
                elif tag_name == "album.disc_total":
                    disc_total = tag_val
                else:
                    frame = id3_frame_class( encoding=3, text=tag_val )
                    self._mp3_obj.tags.add( frame )
            
        tpos_frame = _encode_TPOS_frame( disc_number, disc_total )
        if tpos_frame != None:
            self._mp3_obj.tags.add( tpos_frame )

        trck_frame = _encode_TRCK_frame( track_number, track_total )
        if trck_frame != None:
            self._mp3_obj.tags.add( trck_frame )

        self._add_images( track_info.album_info.images )

    def get_track_info( self ):
        mp3_obj = self._mp3_obj
        track_info = track.TrackInfo()
        self._add_folder_images( track_info )

        for tag_name, id3_frame_class in _TRACK_INFO_TO_ID3.items():
            if ( id3_frame_class != None
                 and mp3_obj.has_key( id3_frame_class.__name__ ) ):
                val = mp3_obj[ id3_frame_class.__name__ ]
                if not track_info.is_multi_value( tag_name ):
                    # important to call unicode() as some values are
                    # not actually strings -- only string like -- and lack
                    # important methods like the default string cmp()
                    track_info[ tag_name ] = unicode(val.text[0])
                else:
                    track_info[ tag_name ] = [ unicode(x) for x in val.text ]

        # id3 combines the number and total into a single field of
        # format: "number/total"
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None
        if id3.TRCK.__name__ in mp3_obj:
            trck = mp3_obj[ id3.TRCK.__name__ ]
            track_number, track_total = _decode_TRCK_frame( trck )
        if id3.TPOS.__name__ in mp3_obj:
            tpos = mp3_obj[ id3.TPOS.__name__ ]        
            disc_number, disc_total = _decode_TPOS_frame( tpos )
        track_info[ "track_number"] = track_number
        track_info[ "track_total" ] = track_total
        track_info[ "disc_number" ] = disc_number
        track_info[ "album.disc_total" ] = disc_total 

        #FIXME: read embedded images

        return track_info

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



