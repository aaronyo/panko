import mutagen.mp4
import logging

from audiobatch.persistence.audiofile import AudioFile
from audiobatch.model import track, album, audiostream, format


_LOGGER = logging.getLogger()

_UNSUPPORTED = "unsupported"
_SPECIAL = "special"

_MP4_TO_COMMON = {
    "\xa9alb"     : "album.title",
    "aART"        : "album.artists",
    "\xa9ART"     : "artists",
    "\xa9wrt"     : "composers",
    "\xa9day"     : "album.release_date",
    _SPECIAL      : "disc_number",
    _SPECIAL      : "disc_total",
    "\xa9gen"     : "genres",
    _UNSUPPORTED  : "isrc",
    "\xa9nam"     : "title",
    _SPECIAL      : "track_number",
    _SPECIAL      : "track_total",
    }

_COMMON_TO_MP4 = dict( [ (v, k) for k, v in _MP4_TO_COMMON.items() ] )

EXTENSIONS = ['m4a', 'mp4']

# Logger's console output is broken for characters that do
# not have an ascii representation.  If we stop using logger for
# console output we can retire this code.  This character leads most
# mp4 tag names.
 
def _cleanse_for_ascii( unclean ):
    
    if unclean.startswith( '\xa9' ):
        return r"\xa9" + unclean.replace( '\xa9' , '', 1 )
    else:
        return unclean


def recognized( path ):
    file_obj = open( path )
    file_header = file_obj.read(128)
    match_score = mutagen.mp4.MP4.score( path, file_obj, file_header )
    file_obj.close()
    return match_score > 0


class MP4File( AudioFile ):
    def __init__( self, path ):
        self._mp4_obj = mutagen.mp4.MP4( path )
        AudioFile.__init__( self, path, self._mp4_obj )

    def get_audio_stream( self ):
        # Mutagen does not provide bitrate for ALAC nor methods for
        # differentiating ALAC and AAC (not that I could find, anyway)
        # FIXME: Needs proper bitrate implementation
        dummy_bitrate = 900000
        mp4_bitrate = self._mp4_obj.info.bitrate
        if mp4_bitrate == 0:
            return audiostream.AudioStream( dummy_bitrate,
                                            format.ALAC_STREAM,
                                            self.path )
        else:
            return audiostream.AudioStream( mp4_bitrate,
                                            audiostream.AAC_STREAM,
                                            self.path )
            


    def _update_album_info( self, album_info ):
        mp4_obj = self._mp4_obj
        for field_name, value in album_info.items():
            if field_name == "images":
                #FIXME: handle saving embedded images in MP4
                continue
            elif field_name == "release_date":
                if value.month != None:
                    _LOGGER.warn( "Can't write extended date information to "
                                  + "MP4 -- only year: %s" % value )
                value = str(value.year)
            lookup_name = "album." + field_name
            try:
                mp4_tag_name = _COMMON_TO_MP4[ lookup_name ]
            except KeyError:
                _LOGGER.error( "Can't write '%s' - MP4 mapping not found"
                               % tag_name )
                continue
            if album_info.is_multi_value( field_name ):
                mp4_obj[ mp4_tag_name ] = value
            else:
                mp4_obj[ mp4_tag_name ] = [value]
            

    def _update_track_info( self, track_info ):
        mp4_obj = self._mp4_obj
        # mp4 combines the number and total into a single "atom"
        # further, it doesn't seem to accept None -- 0 must be provided
        # FIXME: does 0 do the right thing (act as null) according to iTunes
        #        and the mp4 spec?
        disc_number = 0
        disc_total = 0
        track_number = 0
        track_total = 0

        for field_name, value in track_info.items():
            if field_name == "track_number":
                track_number = value
            elif field_name == "track_total":
                track_total = value
            elif field_name == "disc_number":
                disc_number = value
            elif field_name == "disc_total":
                disc_total = value
            else: 
                try:
                    mp4_tag_name = _COMMON_TO_MP4[ field_name ]
                except KeyError:
                    _LOGGER.error( "Can't write '%s' - MP4 mapping not found"
                                   % field_name )
                    continue
                if mp4_tag_name == _UNSUPPORTED:
                    _LOGGER.error( "Can't write '%s' - not standard in MP4"
                                   % field_name )    
                # Mutagen seems to always read encoded tags into a list,
                # but varies on wheter or not it handles non-list input
                # appropriately, so we'll just always use a list
                elif track_info.is_multi_value( field_name ):
                    mp4_obj[ mp4_tag_name ] = value
                else:
                    mp4_obj[ mp4_tag_name ] = [value]
        
        if ( track_number != 0 or track_total != 0 ):
            mp4_obj[ "trkn" ]= [ (track_number, track_total) ]
        if ( disc_number != 0 or disc_total != 0 ):
            mp4_obj[ "disk" ]= [ (disc_number, disc_total) ]            


    def _get_info( self ):
        def _update_field( info, field_name, mp4_value ):
            if info.is_multi_value( field_name ):
                info[ field_name ] = [ unicode(x) for x in mp4_value ]
            else:
                    # important to call unicode() as some values are
                    # not actually strings -- only string like -- and lack
                    # important methods like the default string cmp()
                info[ field_name ] = unicode( mp4_value[0] )

        # FIXME: How are multi vals encoded?  Have seen artists sep by '/'.
        mp4_obj = self._mp4_obj
        track_info = track.TrackInfo()
        album_info = album.AlbumInfo()
        
        for mp4_tag_name, value in mp4_obj.items():
            if mp4_tag_name == "disk":
                first_val = value[0]
                if first_val[0] != 0:
                    track_info[ "disc_number" ] = first_val[0]
                if first_val[1] != 0:
                    track_info[ "disc_total" ] = first_val[1]
            elif mp4_tag_name == "trkn":
                first_val = value[0]
                if first_val[0] != 0:
                    track_info[ "track_number" ] = first_val[0]
                if first_val[1] != 0:
                    track_info[ "track_total" ] = first_val[1]
            else:
                try:
                    field_name = _MP4_TO_COMMON[ mp4_tag_name ]            
                except KeyError:
                    _LOGGER.debug( "Can't read MP4 tag "
                                   + "'%s' - common mapping not found"
                                   % _cleanse_for_ascii(mp4_tag_name) )
                    continue
                if field_name.startswith("album."):
                    field_name = field_name[6:]
                    _update_field( album_info, field_name, value )
                else:
                    _update_field( track_info, field_name, value )

        return album_info, track_info
