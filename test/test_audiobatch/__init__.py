import os
import os.path

from audiobatch.model import format

test_data_dir = os.path.join( os.environ["AUDIOBATCH_HOME"], "test", "data" )

def notags_path( container_format ):
    filename = ( "notags" + os.extsep +
                 format.container_to_ext(container_format) )
    return os.path.join( test_data_dir, filename )
