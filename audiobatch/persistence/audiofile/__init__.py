import os.path
import shutil
import types

from audiobatch.model import image 

def read( path ):
    from audiobatch.persistence.audiofile import flac, mp3, mp4
    _, ext = os.path.splitext( path )
    ext = ext[1:] # drop the "."
    if ext in flac.EXTENSIONS:
        return flac.FLACFile( path )
    elif ext in mp3.EXTENSIONS:
        return mp3.MP3File( path )
    elif ext in mp4.EXTENSIONS:
        return mp4.MP4File( path )
    else:
        raise Exception( "File extension not recognized for file: %s"
                         % path )

class AudioFile( object ):
    """
    AudioFile presents an interface for reading and writing a generic
    tag model, i.e., a TrackInfo object.  Subclasses deal with the conversion
    to specific container formats, and we leverage mutagen to do the heavy
    lifting of the byte level formatting.
    """

    def __init__( self, path, mutagen_obj ):
        self.path = path
        self._mutagen_obj = mutagen_obj
        self._updated_audio_stream = None

    def clear_track_info( self, track_info ):
        raise NotImplementedError

    def get_track_info( self ):
        raise NotImplementedError

    def update_track_info( self, track_info ):
        """ Similar to 'update' on python dictionaries.  Existing values
        not given a new value will remain."""
        raise NotImplementedError

    def get_audio_stream( self ):
        raise NotImplementedError

    def set_audio_stream( self, audio_stream ):
        """ Replaces the underlying audio file with a new version where
        all tags are copied over and only the stream has changed. """
        raise NotImplementedError

    def save( self ):        
        if (     self._updated_audio_stream != None
             and self._updated_audio_stream.path != self.path ):
            stream = self._updated_audio_stream

            # We've got a new stream file.  The existing tags in this new
            # file are largely irrelevant, but for now we won't clear them
            # since we don't have a more deliberate approach to keeping
            # around encoder credits tagged by whatever created the
            # stream.
            # Actually replacing the stream's bytes in place in the 
            # original audio file would be conceptually accurate, but
            # mutagen doesn't provide for this, it would require more
            # disk writes than a rename, and the write could easily fail
            # in the middle (think large file over network) leading to
            # a corrupted audio stream in our library.
            self._copy_tags_to( stream.path )

            # FIXME: ack... I'm going to have to make sure permission bits
            # are always coming out as desired at some point.  This
            # may not be the most relevant place for this note...
            if ( stream.is_temp_path ):
                target_dir = os.path.dirname( self.path )
                if not os.path.isdir( target_dir ):
                    os.makedirs( target_dir )                
                shutil.move( stream.path, self.path )
            else:
                raise ValueError("updated audio streams must ref a temp path")

            # Update the the AudioStream's path member to reflect the
            # move in case this AudioStream is referenced elsewhere.
            stream.path = self.path
            stream.is_temp_path = None
            self._updated_audio_stream = None
        else:
            self._mutagen_obj.save()

    def _add_folder_images( self, track_info ):
        """ For now, only looks for a "cover.jpg" """
        containing_folder = os.path.dirname( self.path )
        cover_path = os.path.join( containing_folder, "cover.jpg" )
        if os.path.isfile( cover_path ):
            track_info.album_info.images = \
                {image.SUBJECT__ALBUM_COVER: image.makeImage( cover_path ) }

    def _copy_tags_to( self, target_path ):
        """ Copy tags to a file of the same format as this AudioFile. """
        mutagen_class = self._mutagen_obj.__class__
        mutagen_obj = mutagen_class( target_path )
        mutagen_obj.update( self._mutagen_obj.items() )
        mutagen_obj.save()

    @staticmethod
    def _unicode_all( val ):
        if type(val) == types.ListType:
            return [ unicode(x) for x in val ]
        else:
            return unicode( val )
        

