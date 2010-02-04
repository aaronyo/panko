#!/usr/bin/env python
import os
import sys
import stat
import fnmatch
import logging
import optparse
import subprocess
import ConfigParser
import shutil
import subprocess
from audiometa import AudioMeta
# import qllib

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
    return os.path.join(homePath, '.audio_batch/audio_batch.ini')


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

        jobConfig = _Config.JobConfig( confParser.get( jobName, "source_dir" ),
                                       extensionsToConvert,
                                       extensionsToCopy,
                                       excludePatterns,
                                       confParser.get( jobName, "target_dir" ) )
        return jobConfig

    confParser = ConfigParser.ConfigParser()
    confParser.read( confFileAbs )

    logFileAbs = confParser.get( "system", "log_file" )
    defaultDecoderSeq = confParser.get( "default_decoder", "command_seq" )
    defaultEncoderSeq = confParser.get( "default_encoder", "command_seq" )
    config = _Config( logFileAbs, defaultDecoderSeq, defaultEncoderSeq )

    jobNames = confParser.options( "jobs" )
    for jobName in jobNames:
        config.jobConfigs[jobName] = _parseJob( confParser, jobName )

    return config

def _allFilePaths(baseDirAbs, extensions=None, excludePatterns=None):

    def _shouldExclude( path, excludePatterns ):
        if excludePatterns == None or len(excludePatterns) == 0:
            return False

        for excludePat in excludePatterns:
            if fnmatch.fnmatch( path, excludePat ):
                return True

        return False

    paths = set()
    for path, subdirs, files in os.walk(baseDirAbs):
        for name in files:
            patterns = []
            if extensions == None:
                patterns.append('*')
            else:
                for ext in extensions:
                    patterns.append('*' + os.extsep + ext)
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    absolutePath = os.path.join(path, name)
                    if not _shouldExclude( absolutePath, excludePatterns ):
                        paths.add( os.path.relpath( absolutePath, baseDirAbs ) )
                    break

    return paths

# leaves the '.' on the end so that file sort order doesn't change
def _strip_extension( path, extensions ):
    for ext in extensions:
        fileSuffix = os.extsep + ext
        if path.endswith( fileSuffix ):
            # leave the '.' on the end so that sorting is not disrupted
            return path[: 1-len(fileSuffix) ]
            break
    
# Determin all adds, replaces and deletes needed for the target folder based
# on changes made to the source folder since the last run
def _determine_updates( sources, targets, sourceDirAbs, targetDirAbs, sourceExtensions, targetExtensions ):
    if sourceExtensions == None or targetExtensions == None:
        raise Exception("Must supply extensions for sources and targets")

    def _needs_replacement( sourcePath, targetPath, sourceDirAbs, targetDirAbs ):
        sourceModTime = os.stat( os.path.join(sourceDirAbs, sourcePath) )[stat.ST_MTIME]
        targetModTime = os.stat( os.path.join(targetDirAbs, targetPath) )[stat.ST_MTIME]
        return sourceModTime > targetModTime

    def _strip_extensions( filePaths, extensions ):
        stripped = []
        for path in filePaths:
            stripped.append( _strip_extension( path, extensions ) )            
        return stripped

    sortedSources = sorted( sources )
    strippedSortedSources = _strip_extensions( sortedSources, sourceExtensions )

    sortedTargets = sorted( targets )
    strippedSortedTargets = _strip_extensions( sortedTargets, targetExtensions )
    
    sourceAdds = []
    sourceReplacements = []
    targetDeletes = []
    numSources = len( strippedSortedSources ) 
    numTargets = len( strippedSortedTargets ) 
    sIdx = 0
    tIdx = 0
    targetMatched = False

    while not (sIdx == numSources and tIdx == numTargets):
        if sIdx == numSources:
            if not targetMatched:
                targetDeletes.append( sortedTargets[tIdx] )
            tIdx += 1
            targetMatched = False
        elif tIdx == numTargets:
            sourceAdds.append( sortedSources[sIdx] )
            sIdx += 1
        else:
            comparison = cmp( strippedSortedSources[sIdx], strippedSortedTargets[tIdx] )
            # This algorithm will not allow duplicate titles to remain in the target folder
            if comparison == 0:
                # Indicate the match so we don't delete the target on the next loop
                targetMatched = True
                if _needs_replacement( sortedSources[sIdx], sortedTargets[tIdx], sourceDirAbs, targetDirAbs ):
                    sourceReplacements.append( sortedSources[sIdx] )
                sIdx += 1
            elif comparison < 0:
                assert(not targetMatched)
                sourceAdds.append( sortedSources[sIdx] )
                sIdx += 1
            elif comparison > 0:
                if not targetMatched:
                    targetDeletes.append( sortedTargets[tIdx] )
                tIdx += 1
                targetMatched = False
    
    return sourceAdds, sourceReplacements, targetDeletes


def _match_extensions( relativePaths, extensions ):
    patterns = set()
    for ext in extensions:
        patterns.add('*' + os.extsep + ext)

    matches = []
    for relPath in relativePaths:
        for pattern in patterns:
            if fnmatch.fnmatch(relPath, pattern):
                matches.append( relPath )
    return matches


def _copy_meta( sourcePathAbs, targetPathAbs ):
    meta = AudioMeta()

    # Get the textual tags from the source file
    meta.readFile( sourcePathAbs )

    # Get the cover image if we have one.
    # Only supports externally saved "cover.jpg"
    sourceDir = os.path.dirname( sourcePathAbs )
    coverFileAbs = os.path.join( sourceDir, "cover.jpg" )
    if os.path.isfile( coverFileAbs ):
        meta.addImage( coverFileAbs )

    meta.writeFile( targetPathAbs )


class FileConverter:
    def __init__( self, decodeStr, encodeStr, localCopyFirst = False ):
        self.decodeStr = decodeStr
        self.encodeStr = encodeStr
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
        # slowly if operating against remote fles.
        # TODO: Determine the file system device type and skip this step if the source and target
        # locations are local.
        if ( self.localCopyFirst ):
            tempSourcePathAbs = localTempCopy( sourcePathAbs )
            pathToConvertAbs = tempSourcePathAbs
        else:
            tempSourcePathAbs = None
            pathToConvertAbs = sourcePathAbs
            

        specificDecodeStr = self.decodeStr.format(inFile="pathToConvertAbs")
        decodeCmd = eval( specificDecodeStr )

        specificEncodeStr = self.encodeStr.format(outFile="targetPathAbs")
        encodeCmd = eval( specificEncodeStr )

        # Use sequences for the commands so that subprocess module gets to worry about special chars
        # in files (rather than my code)

        _logger.debug( " ".join(decodeCmd) + " | " + " ".join(encodeCmd) )

        targetLeafDir = os.path.dirname( targetPathAbs )
        if not os.path.isdir( targetLeafDir ):
            os.makedirs( targetLeafDir )

        decodeProc = subprocess.Popen(decodeCmd, stdout=subprocess.PIPE)
        encodeProc = subprocess.Popen(encodeCmd, stdin=decodeProc.stdout)
        encodeProc.communicate();

        _copy_meta( pathToConvertAbs, targetPathAbs )

        if ( tempSourcePathAbs != None ):
            os.remove( tempSourcePathAbs )
        

def _convert( sourceDir, relPaths, sourceExtensions, targetDirAbs, decodeStr, encodeStr ):

    converter = FileConverter( decodeStr, encodeStr )
    totalCopies = len( relPaths )
    i = 0
    for relPath in relPaths:
        i += 1
        _logger.debug( "Converting %d of %d: %s" % (i, totalCopies, relPath) )
        sourcePathAbs = os.path.join( sourceDir, relPath )
        relPathMinusExtension = _strip_extension( relPath, sourceExtensions )
        targetPathAbs = os.path.join( targetDirAbs, relPathMinusExtension + "mp3" )
        converter.convert( sourcePathAbs, targetPathAbs )
        
        

def _copy( sourceDirAbs, relPaths, targetDirAbs ):
    totalCopies = len( relPaths )
    i = 0
    for relPath in relPaths:
        i += 1
        sourcePathAbs = os.path.join( sourceDirAbs, relPath )
        targetPathAbs = os.path.join( targetDirAbs, relPath )
        _logger.debug( "Copying %d of %d: %s" % (i, totalCopies, relPath) )
            
        targetLeafDir = os.path.dirname( targetPathAbs )
        if not os.path.isdir( targetLeafDir ):
            os.makedirs( targetLeafDir )
                    
        shutil.copyfile( sourcePathAbs, targetPathAbs) 
        break;

def _delete( targetDirAbs, relativePaths ):
    for relPath in relativePaths:
        absPath = os.path.join( targetDirAbs, relPath )
        _logger.debug( "Deleting: %s" % absPath )
        os.remove( absPath )
        

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
    def __init__( self, logFileAbs, defaultDecoder, defaultEncoder ):
        self.jobConfigs = {}
        self.logFileAbs = logFileAbs
        self.defaultDecoderSeq = defaultDecoder
        self.defaultEncoderSeq = defaultEncoder

    def __str__( self ):
        strRep = 'log file: %s\n' % self.logFileAbs
        strRep += 'default decoder sequence: %s\n' % self.defaultDecoderSeq
        strRep += 'default encoder sequence: %s\n' % self.defaultEncoderSeq
        strRep += 'jobs:\n'
        for jobName, jobConfig in self.jobConfigs.items():
            strRep += "  %s:\n" % jobName
            strRep += "    source: %s\n" % jobConfig.sourceDirAbs
            strRep += "    extensions to convert: %s\n" % jobConfig.extensionsToConvert
            strRep += "    extensions to copy: %s\n" % jobConfig.extensionsToCopy
            strRep += "    excluded patterns: %s\n" % jobConfig.excludePatterns
            strRep += "    target: %s" % jobConfig.targetDirAbs
        return strRep
        
    class JobConfig:        
        def __init__( self, sourceDirAbs, extensionsToConvert, extensionsToCopy,
                      excludePatterns, targetDirAbs ):
            self.sourceDirAbs = sourceDirAbs
            self.extensionsToConvert = extensionsToConvert
            if extensionsToCopy == None:
                self.extensionsToCopy = []
            else:
                self.extensionsToCopy = extensionsToCopy
            self.excludePatterns = excludePatterns
            self.targetDirAbs = targetDirAbs


def _isWorkToBeDone( copyList, convertList, deleteList ):
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

def _processJob( jobConfig, decodeSeq, encodeSeq, forceConfirm ):
    allExtensions = jobConfig.extensionsToConvert.union( jobConfig.extensionsToCopy )
    sourcePaths = _allFilePaths( jobConfig.sourceDirAbs,
                                   allExtensions,
                                   jobConfig.excludePatterns )
    sourcePaths = sorted( sourcePaths )

    targetDirExtensions = jobConfig.extensionsToCopy.union(['mp3'])
    targetPaths = _allFilePaths( jobConfig.targetDirAbs,
                                   targetDirExtensions,
                                   jobConfig.excludePatterns )
    targetPaths = sorted( targetPaths )

    sourceAdds, sourceReplacements, targetDeletes = \
        _determine_updates( sourcePaths, targetPaths, jobConfig.sourceDirAbs, jobConfig.targetDirAbs,
                            allExtensions, targetDirExtensions )

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
        relPathsToCopy = _match_extensions( sourceChanges, jobConfig.extensionsToCopy )
        _logger.info( "%4d copies to be done" % len(relPathsToCopy) )
    else: 
        _logger.info( "No extensions chosen to be copied" )
       
    if conversionEnabled:
        relPathsToConvert = _match_extensions( sourceChanges, jobConfig.extensionsToConvert )
        _logger.info( "%4d conversions to be done" % len(relPathsToConvert) )
    else:
        _logger.info( "No extensions chosen to be converted" )

    _logger.info( "%4d matchless target files to be deleted" % len(targetDeletes) )

    if _isWorkToBeDone( relPathsToCopy, relPathsToConvert, targetDeletes ):
        if _isContinueConfirmed( forceConfirm ):
            if copyEnabled:
                _copy( jobConfig.sourceDirAbs, relPathsToCopy, jobConfig.targetDirAbs )

            if conversionEnabled:
                _convert( jobConfig.sourceDirAbs, relPathsToConvert, jobConfig.extensionsToConvert,
                          jobConfig.targetDirAbs, decodeSeq, encodeSeq )

            _delete( jobConfig.targetDirAbs, targetDeletes )
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
        _processJob( jobConfig, config.defaultDecoderSeq, config.defaultEncoderSeq,
                      cmdLineOptions.forceConfirm)


if __name__ == "__main__":
    main(sys.argv)
