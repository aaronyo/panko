import os
import logging
import subprocess
import shutil

_LOGGER = logging.getLogger()


class ShellStreamConverter:
    def __init__( self,
                  default_decode_cmd,
                  decode_cmds_by_extension,
                  encode_cmd,
                  local_copy_first = False ):

        # Defaults to be used if a specific decoder is not specified for a
        # given extension
        self._default_decode_cmd = default_decode_cmd
        self._decode_cmds_by_extension = decode_cmds_by_extension

        self._encode_cmd = encode_cmd

        self._local_copy_first = local_copy_first

    @staticmethod    
    def _local_temp_copy( source_path ):
        filename = os.path.basename( source_path )
        local_copy_path = os.path.join( os.sep, "tmp", filename )
        _LOGGER.debug( 'Making local copy: "%s" to "%s"' \
                           % ( source_path, local_copy_path) )
        shutil.copyfile( source_path, local_copy_path )
        return local_copy_path

    def convert( self, source_path, target_path ):

        if ( self._local_copy_first ):
            # Copy files to a known local location.  Decoding/Encoding
            # processes may run slowly if operating against remote files.
            # FIXME: Not actually convinced this is often a performance
            # improvement
            temp_source_path = \
                ShellStreamConverter._local_temp_copy( source_path )
            path_to_convert = temp_source_path
        else:
            temp_source_path = None
            path_to_convert = source_path
        
        _, ext = os.path.splitext( path_to_convert )
        ext = ext[1:] # drop the '.'
        if ext in self._decode_cmds_by_extension:
            decode_cmd = self._decode_cmds_by_extension[ ext ]
        else:
            decode_cmd = self._default_decode_cmd

        decode_cmd = \
            eval( decode_cmd.format( inFile="path_to_convert" ) )
        encode_cmd = \
            eval( self._encode_cmd.format( outFile="target_path" ) )

        # Use sequences for the commands, rather than a string, so that
        # the subprocess module can deal with escaping special chars in file
        # names when it assembles the shell command

        target_leaf_dir = os.path.dirname( target_path )
        if not os.path.isdir( target_leaf_dir ):
            os.makedirs( target_leaf_dir )

        _LOGGER.debug( "executing: " + " ".join(decode_cmd) )
        subprocess.call(decode_cmd)

        _LOGGER.debug( "executing: " + " ".join(encode_cmd) )
        subprocess.call(encode_cmd)

        if ( temp_source_path != None ):
            os.remove( temp_source_path )
