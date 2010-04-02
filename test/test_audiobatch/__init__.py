import os
import os.path

from audiobatch.model import format

test_data_dir = os.path.join( os.environ["AUDIOBATCH_HOME"], "test", "data" )
temp_data_dir = os.sep + os.path.join( "tmp", "audiobatch" )

if not os.path.exists ( temp_data_dir ):
    os.makedirs( temp_data_dir )

def notags_path( container_format ):
    filename = ( "notags" + os.extsep +
                 format.container_to_ext(container_format) )
    return os.path.join( test_data_dir, filename )

