#!/usr/bin/env python
import os
import sys
import logging
import optparse
import ConfigParser
import audiobatch.meta.convert
import audiobatch.stream.convert
from audiobatch import meta, stream, actions

_logger = logging.getLogger();

def _buildCmdLineParser():
    parser = optparse.OptionParser()

    parser.add_option("-f",
                      "--no-confirmation",
                      action="store_true", 
                      dest="forceConfirm",
                      default=False,
                      help=
"""Supplying this option avoids confirmation or any user input and is
useful for automated runs.  By default, console input is required to
confirm tasks before execution.  """ )

    return parser


def _determineConfigFileAbs():
    homePath = os.path.expanduser('~')
    return os.path.join(homePath, '.audiobatch/audiobatch.ini')


def _parseConfig( confFileAbs ):

    def _parseJob( confParser, jobName ):
        extensionsToConvert = set( confParser.get( jobName, "extensions_to_convert" ).split( ';' ) )

        if confParser.has_option( jobName, "extensions_to_copy" ):
            extensionsToCopy = set( confParser.get( jobName, "extensions_to_copy" ).split( ';' ) )
        else:
            extensionsToCopy = set()

        if confParser.has_option( jobName, "exclude_patterns" ):
            excludePatterns = set( confParser.get( jobName, "exclude_patterns" ).split( ';' ) )
        else:
            excludePatterns = set()

        if confParser.has_option( jobName, "delete_matchless_target_files" ):
            isDeleteEnabled = confParser.getboolean( jobName, "delete_matchless_target_files" )
        else:
            isDeleteEnabled = False

        jobConfig = _Config.JobConfig( confParser.get( jobName, "source_dir" ),
                                       extensionsToConvert,
                                       extensionsToCopy,
                                       excludePatterns,
                                       confParser.get( jobName, "target_dir" ),
                                       isDeleteEnabled )
        return jobConfig

    confParser = ConfigParser.ConfigParser()
    confParser.read( confFileAbs )

    logFileAbs = confParser.get( "system", "log_file" )
    defaultDecoderSeq = confParser.get( "default_decoder", "command_seq" )
    defaultEncoderSeq = confParser.get( "default_encoder", "command_seq" )
    decodersByExtension = {}
    if confParser.has_section( "decoders_by_extension" ):
        for extension, cmdSeq in confParser.items("decoders_by_extension"):
            decodersByExtension[ extension ] = cmdSeq

    config = _Config( logFileAbs, defaultDecoderSeq, defaultEncoderSeq, decodersByExtension )


    jobNames = confParser.options( "jobs" )
    for jobName in jobNames:
        config.jobConfigs[jobName] = _parseJob( confParser, jobName )

    return config

        
def _setupLogging( logFileAbs, isVerbose ):

    logFileAbs = os.path.expanduser( logFileAbs )
    logging.getLogger().setLevel( logging.DEBUG )

    fileHandler = logging.FileHandler( filename = logFileAbs, mode = 'a')
    # We'll always send full debug logging (which really isn't _that_ much)
    # to the file, and only info level to the console unless verbse is
    # requested
    fileHandler.setLevel( logging.DEBUG )
    logFileFormat = "[%(asctime)s, %(levelname)-8s]: %(message)s"
    formatter = logging.Formatter( fmt=logFileFormat,
                                   datefmt="%m-%d %H:%M" )
    fileHandler.setFormatter( formatter )
    logging.getLogger().addHandler( fileHandler )

    # We use a logger to handle console output
    console = logging.StreamHandler( sys.stdout )
    if isVerbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)

    # set a format which is simpler for console use
    formatter = logging.Formatter("[%(levelname)-8s]: %(message)s")
    # tell the handler to use this format
    console.setFormatter(formatter)

    # add the handler to the root logger
    logging.getLogger().addHandler(console)

    if not isVerbose:
        _logger.info( "For verbose/debug output use '-b' or see log file: " + logFileAbs )


class _Config:
    def __init__( self, logFileAbs, defaultDecoder, defaultEncoder, decodersByExtension ):
        self.jobConfigs = {}
        self.logFileAbs = logFileAbs
        self.defaultDecoderSeq = defaultDecoder
        self.defaultEncoderSeq = defaultEncoder
        self.decodersByExtension = decodersByExtension

    def __str__( self ):
        strRep = 'log file: %s\n' % self.logFileAbs
        strRep += 'default decoder sequence: %s\n' % self.defaultDecoderSeq
        strRep += 'default encoder sequence: %s\n' % self.defaultEncoderSeq
        for ext, seq in self.decodersByExtension.items():            
            strRep += '%s decoder sequence: %s\n' % (ext, seq)
        strRep += 'jobs:\n'
        for jobName, jobConfig in self.jobConfigs.items():
            strRep += "  %s:\n" % jobName
            strRep += "    source: %s\n" % jobConfig.sourceDirAbs
            strRep += "    extensions to convert: %s\n" % jobConfig.extensionsToConvert
            strRep += "    extensions to copy: %s\n" % jobConfig.extensionsToCopy
            strRep += "    excluded patterns: %s\n" % jobConfig.excludePatterns
            strRep += "    target: %s\n" % jobConfig.targetDirAbs
            strRep += "    delete matchless target files: %s" % str(jobConfig.isDeleteEnabled)
        return strRep
        
    class JobConfig:        
        def __init__( self, sourceDirAbs, extensionsToConvert, extensionsToCopy,
                      excludePatterns, targetDirAbs, isDeleteEnabled ):
            self.sourceDirAbs = sourceDirAbs
            self.extensionsToConvert = extensionsToConvert
            if extensionsToCopy == None:
                self.extensionsToCopy = []
            else:
                self.extensionsToCopy = extensionsToCopy
            self.excludePatterns = excludePatterns
            self.targetDirAbs = targetDirAbs
            self.isDeleteEnabled = isDeleteEnabled


def _isWorkToBeDone( copyList, convertList, deleteList, isDeleteEnabled ):
    if not isDeleteEnabled:
        deleteList = []

    if len(copyList) + len(convertList) + len(deleteList) > 0:
        return True
    else:
        return False

def _isContinueConfirmed( forceConfirm ):
    if forceConfirm:
        return True
    else:
        print( "Continue with identified tasks?" )
        isConfirmed = raw_input( "['y' to continue] > " ) == 'y'
        return isConfirmed

def _processJob( jobConfig, defaultDecodeSeq, defaultEncodeSeq, decodersByExtension, forceConfirm ):
    allExtensions = jobConfig.extensionsToConvert.union( jobConfig.extensionsToCopy )
    sourcePaths = actions.findPaths( jobConfig.sourceDirAbs, allExtensions, jobConfig.excludePatterns )
    sourcePaths = sorted( sourcePaths )

    targetDirExtensions = jobConfig.extensionsToCopy.union(['mp3'])
    targetPaths = actions.findPaths( jobConfig.targetDirAbs, targetDirExtensions, jobConfig.excludePatterns )
    targetPaths = sorted( targetPaths )

    sourceAdds, sourceReplacements, targetDeletes = \
        actions.determineExtensionIgnorantDiff( sourcePaths, targetPaths,
                                                jobConfig.sourceDirAbs, jobConfig.targetDirAbs )

    _logger.info( "%4d sources not found in target directory" % len(sourceAdds) )
    _logger.info( "%4d sources changed since corresponding target created" % len(sourceReplacements) )

    # We process adds and replaces the same way -- replaces just end up leading to overwriting an 
    # existing file
    sourceChanges = []
    sourceChanges.extend(sourceAdds)
    sourceChanges.extend(sourceReplacements)

    copyEnabled = len( jobConfig.extensionsToCopy ) > 0
    conversionEnabled = len( jobConfig.extensionsToConvert ) > 0

    if copyEnabled:
        relPathsToCopy = actions.matchExtensions( sourceChanges, jobConfig.extensionsToCopy )
        _logger.info( "%4d copies to be done" % len(relPathsToCopy) )
    else: 
        _logger.info( "No extensions chosen to be copied" )
       
    if conversionEnabled:
        relPathsToConvert = actions.matchExtensions( sourceChanges, jobConfig.extensionsToConvert )
        _logger.info( "%4d conversions to be done" % len(relPathsToConvert) )
    else:
        _logger.info( "No extensions chosen to be converted" )

    if jobConfig.isDeleteEnabled:
        _logger.info( "%4d matchless target files to be deleted" % len(targetDeletes) )

    if _isWorkToBeDone( relPathsToCopy, relPathsToConvert, targetDeletes, jobConfig.isDeleteEnabled ):
        if _isContinueConfirmed( forceConfirm ):
            if copyEnabled:
                actions.copyPaths( jobConfig.sourceDirAbs, relPathsToCopy, jobConfig.targetDirAbs )

            if conversionEnabled:
                streamConverter = stream.convert.ShellStreamConverter( defaultDecodeSeq,
                                                                       defaultEncodeSeq,
                                                                       decodersByExtension )
                metaConverter = meta.convert.BasicMetaConverter()
                streamErrors, metaErrors = actions.convertPaths( jobConfig.sourceDirAbs, relPathsToConvert,
                                                                 jobConfig.targetDirAbs, streamConverter,
                                                                 metaConverter)
                for pathAbs, se in streamErrors.items():
                    _logger.error( "Problem converting stream for %s: %s" % (pathAbs, se) );
                for pathAbs, me in metaErrors.items():
                    _logger.error( "Problem converting metadata for %s: %s" % (pathAbs, me) );

            if jobConfig.isDeleteEnabled:
                actions.deletePaths( jobConfig.targetDirAbs, targetDeletes )
    else:
        _logger.info( "There is nothing to do for this job." )


def main(args):    
    cmdLineParser = _buildCmdLineParser()
    (cmdLineOptions, cmdLineArgs) = cmdLineParser.parse_args(args[1:])

    confFileAbs = _determineConfigFileAbs()
    config = _parseConfig( confFileAbs )
    _setupLogging( config.logFileAbs, isVerbose = True )
    _logger.info( "Config:\n%s" % config)

    for jobName, jobConfig in config.jobConfigs.items():
        _logger.info( "Processing job: %s" % jobName )
        _processJob( jobConfig,
                     config.defaultDecoderSeq,
                     config.defaultEncoderSeq,
                     config.decodersByExtension,
                     cmdLineOptions.forceConfirm)


if __name__ == "__main__":
    main(sys.argv)
