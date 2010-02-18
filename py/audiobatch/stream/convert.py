import os
import logging
import subprocess

_logger = logging.getLogger();


class ShellStreamConverter:
    def __init__( self, decodeCmdTemplate, encodeCmdTemplate, decodersByExtension, localCopyFirst = False ):

        # Defaults to be used if a specific decoder is not specified for a given extension
        self.decodeCmdTemplate = decodeCmdTemplate
        self.encodeCmdTemplate = encodeCmdTemplate

        self.decodeCmdTemplateByExtension = decodersByExtension

        self.localCopyFirst = localCopyFirst

    @staticmethod
    def _localTempCopy( fileAbs ):
        filename = os.path.basename( fileAbs )
        localCopyAbs = os.path.join( os.sep, "tmp", filename )
        _logger.debug( 'Making local copy: "%s" to "%s"' % (fileAbs, localCopyAbs) )
        shutil.copyfile( fileAbs, localCopyAbs )
        return localCopyAbs

    def convert( self, sourcePathAbs, targetPathAbs ):

        # Copy files to a known local location.  Decoding/Encoding processes may run
        # slowly if operating against remote files.
        # TODO: Determine the file system device type and skip this step if the source and target
        # locations are local.  (maybe just remove this entirely)
        if ( self.localCopyFirst ):
            tempSourcePathAbs = localTempCopy( sourcePathAbs )
            pathToConvertAbs = tempSourcePathAbs
        else:
            tempSourcePathAbs = None
            pathToConvertAbs = sourcePathAbs
        
        root, ext = os.path.splitext( pathToConvertAbs )
        ext = ext[1:] # drop the '.'
        if ext in self.decodeCmdTemplateByExtension:
            decodeCmdTemplate = self.decodeCmdTemplateByExtension[ ext ]
        else:
            decodeCmdTemplate = self.decodeCmdTemplate

        decodeCmdSeq = eval( decodeCmdTemplate.format(inFile="pathToConvertAbs") )
        encodeCmdSeq = eval( self.encodeCmdTemplate.format(outFile="targetPathAbs") )

        # Use sequences for the commands so that subprocess module handles special chars
        # in files

        targetLeafDir = os.path.dirname( targetPathAbs )
        if not os.path.isdir( targetLeafDir ):
            os.makedirs( targetLeafDir )

        _logger.debug( "executing: " + " ".join(decodeCmdSeq) )
        decodeProc = subprocess.call(decodeCmdSeq)

        _logger.debug( "executing: " + " ".join(encodeCmdSeq) )
        encodeProc = subprocess.call(encodeCmdSeq)

#        _logger.debug( " ".join(decodeCmdSeq) + " | " + " ".join(encodeCmdSeq) )
#
#        targetLeafDir = os.path.dirname( targetPathAbs )
#        if not os.path.isdir( targetLeafDir ):
#            os.makedirs( targetLeafDir )
#
#        decodeProc = subprocess.Popen(decodeCmdSeq, stdout=subprocess.PIPE)
#        encodeProc = subprocess.Popen(encodeCmdSeq, stdin=decodeProc.stdout)
#        encodeProc.communicate();

        if ( tempSourcePathAbs != None ):
            os.remove( tempSourcePathAbs )
