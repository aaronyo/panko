import os
import stat
import shutil
import types
import logging
import datetime
import StringIO
import copy
import PIL.Image

from .. import model

_LOGGER = logging.getLogger()

def open_audio_file(path):
    from . import flac, mp3, mp4
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

def read_track(path, cover_art=None):
    audio_file = open_audio_file(path)
    mod_time = datetime.datetime.fromtimestamp( os.stat(path)[stat.ST_MTIME] )
    image_ref = None
    if cover_art:
        cover_path = os.path.join(os.path.dirname(path), cover_art)
        if os.path.exists(cover_path):
            image_ref = model.track.PathImageRef(cover_path)
            
    return model.track.Track( path,
                              mod_time,
                              audio_file.get_tags(),
                              audio_file.get_raw_tags(),
                              image_ref )

def write_tags(path, tags, clear=False):
    audio_file = open_audio_file(path)
    if clear:
        audio_file.clear_tags()
    audio_file.update_tags(tags)
    audio_file.save()

def read_folder_image(track_path, filename=None):
    dir_ = os.path.dirname(track_path)
    path = os.path.join(dir_, filename)

    format = os.path.splitext(path)[1][1:].lower()
    format = 'jpeg' if format == 'jpg' else format
    return Image( open(path).read(), format )
    
def embed_cover_art(track_path, image):
    audio_file = open_audio_file(track_path)
    audio_file.embed_cover_art(image)
    audio_file.save()
    
def extract_cover_art(track_path):
    return open_audio_file(track_path).extract_cover_art()

class Image( object ):        
    def __init__( self, bytes, format ):
        self.bytes = bytes
        if format.startswith('image/'):
            format = format[6:]
        self.format = format.lower()

    def __eq__(self, other):
       return self.bytes == other.bytes and self.format == other.format

    @staticmethod
    def from_pil_image( pil_image, format ):
        buf = StringIO.StringIO()
        pil_image.save(buf, format = format or pil_image.format)
        bytes = buf.getvalue()
        buf.close()
        return Image(bytes, pil_image.format)
        
    def pil_image(self):
        pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
        pil_image.format = self.format
        return pil_image

    def dimensions( self ):
        return self._pil_image().size

    def mime_type( self, shorten=False ):
        return self.format

    def full_mime_type(self):
        return "image/" + self.format.lower()

    def conform_size( self, max_side_length ):
        '''Returns a copy conforming to max_side_length'''
        pil_image = PIL.Image.open( StringIO.StringIO(self.bytes) )
        width, height = pil_image.size
        if width >= height:
            if width > max_side_length:
                target_width = max_side_length
                target_height = int( (float(target_width) / width) * height )
        elif height > max_side_length:
            target_height = max_side_length
            target_width = int ( (float(target_height) / height) * width )

        if target_width != None:
            new_pil_image = pil_image.resize( (target_width, target_height),
                                              PIL.Image.ANTIALIAS )
            return Image.from_pil_image( new_pil_image, self.format )
        else:
            return Image( copy.deepcopy(self.bytes), self.format )
            

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
        
    def get_tags( self ):
        raise NotImplementedError

    def update_tags( self, track_info ):
        raise NotImplementedError

    def get_audio_stream( self ):
        raise NotImplementedError

    def set_audio_stream( self, audio_stream ):
        raise NotImplementedError

    def _embed_cover_art( self, bytes, mime_type ):
        raise NotImplementedError

    def _extract_cover_art( self ):
        raise NotImplementedError

    def embed_cover_art( self, img ):
        self._embed_cover_art(img.bytes, img.full_mime_type())

    def extract_cover_art(self):
        return Image(* self._extract_cover_art())

    def clear_tags( self ):
        self._mutagen_obj.delete()

    def get_raw_tags( self ):
        return dict(self._mutagen_obj)

    def save( self ):
            self._mutagen_obj.save()

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
