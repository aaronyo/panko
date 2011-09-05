from mutagen import mp3, id3
import logging
import StringIO
import shutil

from . import AudioFile
from audiobatch.model import track

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

_ID3_COVER_ART_CODE = 3

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

def _split_TRCK_frame( frame ):
    vals = frame.text[0].split("/")
    return vals[0], vals[1] if len(vals) > 1 else None

def _split_TPOS_frame( frame ):
    vals = frame.text[0].split("/")
    return vals[0], vals[1] if len(vals) > 1 else None


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

    def update_tags( self, tags ):
        if self._mp3_obj.tags == None:
            self._mp3_obj.add_tags()

        # id3 combines the number and total into a single field of
        # format: "number/total"
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        flat_tags = track.TagSet.flatten(tags)
        for field_name, value in flat_tags.items():
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
                    if field_name == "album.release_date":
                        value = str( value )
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

    def get_tags( self ):
        tags = track.TrackTagSet()
        mp3_obj = self._mp3_obj
        
        disc_number = None
        disc_total = None
        track_number = None
        track_total = None

        for tag_name, value in mp3_obj.items():
            if tag_name in _ID3_TO_COMMON:
                value_unicode = [unicode(t) for t in value.text]
                tags.parse(_ID3_TO_COMMON[ tag_name ], value_unicode )
            # id3 combines the number and total into a single field of
            # format: "number/total"
            elif tag_name == id3.TRCK.__name__:
                track_number, track_total = _split_TRCK_frame( value )
            elif tag_name == id3.TPOS.__name__:
                disc_number, disc_total = _split_TPOS_frame( value )
            else:
                _LOGGER.debug( "Can't read MP3 tag "
                               + "'%s' - common mapping not found"
                               % tag_name )

        tags.parse("track_number", track_number)
        tags.parse("track_total", track_total)
        tags.parse("disc_number", disc_number)
        tags.parse("disc_total", disc_total )

        return tags


    def _embed_cover_art( self, bytes, mime_type ):
        apicFrame = id3.APIC( encoding = 3,
                              mime = mime_type,
                              type = _ID3_COVER_ART_CODE,
                              desc = 'cover',
                              data = bytes )
        self._mp3_obj.tags.add( apicFrame )        

    def _extract_cover_art( self ):
        art = self._mp3_obj.tags[id3.APIC.__name__+':cover']
        return art.data, art.mime

    def __repr__( self ):
        return self._mp3_obj.__repr__()



