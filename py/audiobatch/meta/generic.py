import os.path
import copy

from PIL import Image

from audiobatch.meta import flac, mp3, m4a

IMAGE_SUBJECT__ALBUM_COVER = "album_cover"


def read_audio_file( path ):
    if flac.recognized( path ):
        return flac.FlacFile( path )
    elif mp3.recognized( path ):
        return mp3.Mp3File( path )
    elif m4a.recognized( path ):
        return m4a.M4aFile( path )
    else:
        raise Exception( "File type not recognized for file: %s" \
                             % path )


class TrackMeta:

    def __init__( self ):
        self.tags = {}
        self.images = {}
        self.image_output_encoding = "jpeg"
        self.bitrate = None

    def read_file( self, path, tags=True, images=False ):
        audio_file = read_audio_file( path )

        if tags:
            self.tags.update( audio_file.get_tags() )
        if images:
            raise Exception( "Extracting images from an audio file is not " +
                             "yet supported" )
            
    def write_file( self,
                    path,
                    clear_first=False,
                    tags=True,
                    images=True ):
        audio_file = read_audio_file( path )

        if clear_first:
            audio_file.clear_all()
        if tags and len( self.tags ) > 0:
            audio_file.add_tags( self.tags )
        if images and len( self.images ) > 0:
            audio_file.add_images( self.images, self.image_output_encoding )

        audio_file.save()

    def add_tag( self, tag_name, tag_value ):
        self.tags[ tag_name ] = tag_value

    def add_image( self, image_file_abs, max_side_length=None, subject=None ):
        filename = os.path.basename( image_file_abs )
        if subject == None:
            if filename.startswith("cover"):
                subject = IMAGE_SUBJECT__ALBUM_COVER
            else:
                raise Exception( "Unable to determine image subject from " +
                                 "filename: %s" % image_file_abs )

        image = Image.open( image_file_abs )
        if max_side_length != None:
            image = TrackMeta._conform_size( image, max_side_length )
            
        self.images[subject] = image
        
    @staticmethod
    def _conform_size( image, max_side_length ):
        width, height = image.size
        if width >= height:
            if width > max_side_length:
                target_width = max_side_length
                target_height = int( (float(target_width) / width) * height )
        else:
            if height > max_side_length:
                target_height = max_side_length
                target_width = int ( (float(target_height) / height) * width )
        
        if target_width != None:
            return image.resize( (target_width, target_height),
                                 Image.ANTIALIAS )
        else:
            # make a copy so that this function doesn't sometimes return
            # a copy and sometimes return a ref to the input image
            return copy.deepcopy(image)
