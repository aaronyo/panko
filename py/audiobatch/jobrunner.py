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

_LIST_SEP = ';'

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

        #
        # required config params
        #

        sourceDir = confParser.get( jobName, "source_dir" )
        targetDir = confParser.get( jobName, "target_dir" )
        audioExtensions = confParser.get( jobName, "audio_extensions" ).split( _LIST_SEP )
        # strip whitespace and remove duplicates
        audioExtensions = set( [ x.strip() for x in audioExtensions ] )

        #
        # optional config params -- checked for existence
        #

        if confParser.has_option( jobName, "convert_condition" ):
            convertCondition = confParser.get( jobName, "convert_condition" )
        else:
            convertCondition = None

        if confParser.has_option( jobName, "copy_condition" ):
            copyCondition = confParser.get( jobName, "copy_condition" )
        else:
            copyCondition = None

        if confParser.has_option( jobName, "exclude_patterns" ):
            excludePatterns = confParser.get( jobName, "exclude_patterns" ).split( _LIST_SEP )
            # strip whitespace and remove duplicates
            excludePatterns = set( [ x.strip() for x in excludePatterns ] )
        else:
            excludePatterns = set()

        if confParser.has_option( jobName, "delete_matchless_target_files" ):
            isDeleteEnabled = confParser.getboolean( jobName, "delete_matchless_target_files" )
        else:
            isDeleteEnabled = False

        jobConfig = _Config.JobConfig( sourceDir,
                                       targetDir,
                                       audioExtensions,
                                       excludePatterns,
                                       convertCondition,
                                       copyCondition,
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
            strRep += "    target: %s\n" % jobConfig.targetDirAbs
            strRep += "    audio extensions: %s\n" % jobConfig.audioExtensions
            strRep += "    excluded patterns: %s\n" % jobConfig.excludePatterns
            strRep += "    convert condition: %s\n" % jobConfig.convertCondition
            strRep += "    copy condition: %s\n" % jobConfig.copyCondition
            strRep += "    delete matchless target files: %s" % str(jobConfig.isDeleteEnabled)
        return strRep
        
    class JobConfig:        
        def __init__( self, sourceDirAbs, targetDirAbs, audioExtensions, excludePatterns, convertCondition,
                      copyCondition, isDeleteEnabled ):
            self.sourceDirAbs = sourceDirAbs
            self.targetDirAbs = targetDirAbs
            self.audioExtensions = audioExtensions
            self.excludePatterns = excludePatterns
            self.convertCondition = convertCondition
            self.copyCondition = copyCondition
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
    _logger.info( "indexing source paths..." )
    sourcePaths = actions.findPaths( jobConfig.sourceDirAbs, jobConfig.audioExtensions, jobConfig.excludePatterns )
    sourcePaths = sorted( sourcePaths )

    _logger.info( "indexing target paths..." )
    targetPaths = actions.findPaths( jobConfig.targetDirAbs, jobConfig.audioExtensions, jobConfig.excludePatterns )
    targetPaths = sorted( targetPaths )

    _logger.info( "diffing source and target paths..." )
    newSources, updatedSources, matchlessTargets = \
        actions.extensionIgnorantDiff( sourcePaths, targetPaths,
                                       jobConfig.sourceDirAbs, jobConfig.targetDirAbs )

    _logger.info( "%4d sources not found in target directory" % len( newSources ) )
    _logger.info( "%4d sources changed since corresponding target created" % len( updatedSources ) )

    # We process adds and replaces the same way -- replaces just end up leading to overwriting an 
    # existing file
    sourceChanges = []
    sourceChanges.extend( newSources )
    sourceChanges.extend( updatedSources )

    if jobConfig.convertCondition != None:
        conversionEnabled = True
        pathsToConvert, pathsRemaining = \
            actions.filterPaths( sourceChanges, jobConfig.sourceDirAbs, jobConfig.convertCondition )
        _logger.info( "%4d conversions to be done" % len( pathsToConvert ) )
    else:
        conversionEnabled = False
        _logger.info( "Converting disabled; no condition set for selecting files to be converted" )

    if jobConfig.copyCondition != None:
        copyEnabled = True
        pathsToCopy, pathsIgnored = \
            actions.filterPaths( pathsRemaining, jobConfig.sourceDirAbs, jobConfig.copyCondition )
        _logger.info( "%4d copies to be done" % len( pathsToCopy ) )
    else: 
        copyEnabled = False
        _logger.info( "Copying disabled; no condition set for selecting files to be copied" )
       
    if jobConfig.isDeleteEnabled:
        _logger.info( "%4d matchless target files to be deleted" % len( matchlessTargets ) )

    if _isWorkToBeDone( pathsToCopy, pathsToConvert, matchlessTargets , jobConfig.isDeleteEnabled ):
        if _isContinueConfirmed( forceConfirm ):

            # Copies are faster, so let's get them out of the way first
            if copyEnabled:
                actions.copyPaths( jobConfig.sourceDirAbs, pathsToCopy, jobConfig.targetDirAbs )

            if conversionEnabled:
                streamConverter = stream.convert.ShellStreamConverter( defaultDecodeSeq,
                                                                       defaultEncodeSeq,
                                                                       decodersByExtension )
                metaConverter = meta.convert.BasicMetaConverter()
                for streamError, metaError in actions.convertPaths( jobConfig.sourceDirAbs, pathsToConvert,
                                                                    jobConfig.targetDirAbs, streamConverter,
                                                                    metaConverter ):
                    if streamError != None:
                        _logger.error( "Problem converting stream for %s: %s" % (pathAbs, streamError) );
                    if metaError != None:
                        _logger.error( "Problem converting metadata for %s: %s" % (pathAbs, metaError) );

            if jobConfig.isDeleteEnabled:
                actions.deletePaths( jobConfig.targetDirAbs, matchlessTargets )
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
