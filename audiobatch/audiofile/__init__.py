import os
import stat
import shutil
import types
import logging

from audiobatch.model import image, track

_LOGGER = logging.getLogger()

def open(path):
    from . import flac, mp3
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

def update(path, tags=None, images=None):
    pass

def convert(path, target_path, format, tags=None, images=None):
    pass

def read_track(path):
    audio_file = open(path)
    mod_time = os.stat(path)[stat.ST_MTIME]
    return track.Track(path, mod_time, audio_file.get_tags(), audio_file.get_raw_tags())
        
def scan( self,
          base_dir_abs,
          extensions = None,
          exclude_patterns = None,
          return_rel_path = True ):
    ''' Return paths of audio files found beneath the designated base directory '''

    paths = set()
    for path, _, files in os.walk(base_dir_abs):
        for name in files:
            patterns = []
            if extensions == None:
                patterns.append('*')
            else:
                for ext in extensions:
                    patterns.append('*' + os.extsep + ext)
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    absolute_path = os.path.join(path, name)
                    if not TrackRepository._should_exclude(
                        absolute_path,
                        exclude_patterns ):
                        if return_rel_path:
                            paths.add( os.path.relpath( absolute_path,
                                                        base_dir_abs ) )
                        else:
                            paths.add( absolute_path )
                    break

    return paths

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

    def clear_tags( self, track_info ):
        raise NotImplementedError

    def get_tags( self ):
        raise NotImplementedError

    def update_tags( self, track_info ):
        raise NotImplementedError

    def get_audio_stream( self ):
        raise NotImplementedError

    def set_audio_stream( self, audio_stream ):
        """ Replaces the underlying audio file with a new version where
        all tags are copied over and only the stream has changed. """
        self._updated_audio_stream = audio_stream

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

    def _add_folder_images( self, album_info ):
        """ For now, only looks for a "cover.jpg" """
        containing_folder = os.path.dirname( self.path )
        cover_path = os.path.join( containing_folder, "cover.jpg" )
        if os.path.isfile( cover_path ):
            if image.SUBJECT__ALBUM_COVER in album_info.images:
                _LOGGER.warn( "Reading folder image instead of already"
                              + " found image: %s, %s"
                              % ( image.SUBJECT__ALBUM_COVER, self.path ) )
            album_info.images = \
                {image.SUBJECT__ALBUM_COVER: image.makeImage( cover_path ) }

    def _copy_tags_to( self, target_path ):
        """ Copy tags to a file of the same format as this AudioFile. """
        mutagen_class = self._mutagen_obj.__class__
        mutagen_obj = mutagen_class( target_path )
        mutagen_obj.update( self._mutagen_obj.items() )
        mutagen_obj.save()

    @staticmethod
    def _unicode_all( val ):
        if not isinstance(val, basestring) and has_attr(val, '__iter__'):
            return [ unicode(x) for x in val ]
        else:
            return unicode( val )
