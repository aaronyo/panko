import os.path
from audiobatch.meta.generic import TrackMeta

class BasicMetaConverter:
    def __init__( self, embed_folder_images=False ):
        self._embed_folder_images = embed_folder_images

    def convert( self, source_path, target_path ):
        track_meta = TrackMeta()

        # Get the textual tags from the source file
        track_meta.read_file( source_path )

        if self._embed_folder_images:
            # Get the cover image if we have one.
            # Only supports externally saved "cover.jpg"
            source_dir = os.path.dirname( source_path )
            cover_path = os.path.join( source_dir, "cover.jpg" )
            if os.path.isfile( cover_path ):
                track_meta.add_image( cover_path )

        track_meta.write_file( target_path )
