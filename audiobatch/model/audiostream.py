import os
import os.path
import logging
import subprocess
from audiobatch.model import format

_LOGGER = logging.getLogger()
    

class AudioStream( object ):
    """ AudioStream provides the actual stream and related meta data.  The
    stream is generally represented as a path.  The path is likely a fully
    realized audio container, containing tags, etc, but we're only
    concerned with the stream data.  

    The path should be considered a transient property.  It might change,
    because some operation decided to move it -- e.g. when a new
    stream gets persisted in a library.  However, the stream is
    still the "same."  The path itself is not the value we are interested
    in when considering equality, etc. -- the bytes of the stream itself
    is what is important..

    This means if we do decide to provide an __eq__() type method, we'll
    need to actulaly inspect the stream.  There's probably
    some threshold of data we could read, to compute a hash, that is the
    right balance of uniqueness and performance. """
    def __init__( self, bitrate, format, path ):
         self.bitrate = bitrate
         self.format = format
         self.path = path
         self.is_temp_path = False


_ffmpeg_decode_cmd = "['ffmpeg', '-i', {inFile}, '-f', 'wav', {midFile}]"
_sox_decode_cmd = "['sox', '-S', {inFile}, '-t', 'wav', {midFile}]"
_lame_mp3_encode_cmd = "['lame', '-V0', {midFile}, {outFile}]"


def make_converter( default_decode_cmd = _ffmpeg_decode_cmd,
                    decode_cmds_by_format = { format.FLAC_STREAM :
                                                  _sox_decode_cmd },
                    encode_cmd = _lame_mp3_encode_cmd,
                    diagnositc_out = None ):
    return _ShellStreamConverter( default_decode_cmd,
                                  decode_cmds_by_format,
                                  encode_cmd )


# Includes infrastructure detail.  Should be moved out of model package.
class _ShellStreamConverter ( object ):
    def __init__( self,
                  default_decode_cmd,
                  decode_cmds_by_format,
                  encode_cmd ):

        # Defaults to be used if a specific decoder is not specified for a
        # given format
        self._default_decode_cmd = default_decode_cmd
        self._decode_cmds_by_format = decode_cmds_by_format

        self._encode_cmd = encode_cmd

    @staticmethod
    def _temp_stream_filename( target_format ):
        ext = format.stream_to_ext( target_format )
        # FIXME -- better way to do this to avoid security warning?  Could
        # create the file, ensuring perms are as desired, then force encoder
        # to overwrite, but that may require per encoder handling.
        return os.tmpnam() + os.extsep + ext

    def convert( self, stream, target_format ):

        source_path = stream.path
        target_path = _ShellStreamConverter._temp_stream_filename(
            target_format )
        mid_path = _ShellStreamConverter._temp_stream_filename(
            format.WAV_STREAM )
        
        if stream.format in self._decode_cmds_by_format:
            decode_cmd = self._decode_cmds_by_format[ stream.format ]
        else:
            decode_cmd = self._default_decode_cmd

        decode_cmd = \
            eval( decode_cmd.format( inFile = "source_path",
                                     midFile = "mid_path" ) )
        encode_cmd = \
            eval( self._encode_cmd.format( outFile = "target_path",
                                           midFile = "mid_path" ) )

        # Use sequences for the commands, rather than a string, so that
        # the subprocess module can deal with escaping special chars in file
        # names when it assembles the shell command

        target_leaf_dir = os.path.dirname( target_path )
        if not os.path.isdir( target_leaf_dir ):
            os.makedirs( target_leaf_dir )

        _LOGGER.debug( "executing: " + " ".join(decode_cmd) )
        # FIXME: vulnerable to symlink attack
        subprocess.call( decode_cmd )

        _LOGGER.debug( "executing: " + " ".join(encode_cmd) )
        subprocess.call( encode_cmd )
        
        from audiobatch.persistence import audiofile
        new_audio_file = audiofile.read( target_path )
        new_stream = new_audio_file.get_audio_stream()
        new_stream.is_temp_path = True

        return new_stream