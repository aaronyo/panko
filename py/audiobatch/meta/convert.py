import os.path
from audiobatch.meta.generic import TrackMeta

class BasicMetaConverter:
    def __init__():
        pass

    def copyMeta( sourcePathAbs, targetPathAbs ):
        trackMeta = TrackMeta()

        # Get the textual tags from the source file
        trackMeta.readFile( sourcePathAbs )

        # Get the cover image if we have one.
        # Only supports externally saved "cover.jpg"
        sourceDir = os.path.dirname( sourcePathAbs )
        coverFileAbs = os.path.join( sourceDir, "cover.jpg" )
        if os.path.isfile( coverFileAbs ):
            trackMeta.addImage( coverFileAbs )

        trackMeta.writeFile( targetPathAbs )




