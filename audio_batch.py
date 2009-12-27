#!/usr/bin/env python
import os
import sys
import fnmatch
import logging
import optparse
import subprocess
import ConfigParser
import shutil
import subprocess

_logger = logging.getLogger();

def _buildCmdLineParser():
    parser = OptionParser.OptionParser()

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
                                       confParser.get( jobName, "target_dir" ),
                                       confParser.get( jobName, "shell_cmd" ) )
        return jobConfig

    confParser = ConfigParser.ConfigParser()
    confParser.read( confFileAbs )

    logFileAbs = confParser.get("system", "log_file")
    config = _Config( logFileAbs )

    jobNames = confParser.options( "jobs" )
    for jobName in jobNames:
        config.jobConfigs[jobName] = _parseJob( confParser, jobName )

    return config

def _all_file_paths(baseDirAbs, extensions=None, excludePatterns=None):

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
    

def _determine_adds_and_deletes( sources, targets, sourceExtensions, targetExtensions ):
    if sourceExtensions == None or targetExtensions == None:
        raise Exception("Must supply extensions to ignore")

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
                sIdx += 1
                # Indicate the match so we don't delete the taret on the next loop
                targetMatched = True
            elif comparison < 0:
                assert(not targetMatched)
                sourceAdds.append( sortedSources[sIdx] )
                sIdx += 1
            elif comparison > 0:
                if not targetMatched:
                    targetDeletes.append( sortedTargets[tIdx] )
                tIdx += 1
                targetMatched = False
    
    return sourceAdds, targetDeletes


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


def _convertToMp3( sourceDir, relPaths, sourceExtensions, targetDir ):
    totalCopies = len( relPaths )
    if totalCopies > 0:
        i = 0
        for relPath in relPaths:
            i+=1
            sourcePathAbs = os.path.join( sourceDir, relPath )
            relPathMinusExtension = _strip_extension( relPath, sourceExtensions )
            targetPathAbs = os.path.join( targetDir, relPathMinusExtension + "mp3" )
            # Use sequences for the commands so that subprocess module gets to worry about special chars
            # in files (rather than my code)
            decodeCmd = ['ffmpeg', '-i', sourcePathAbs, '-f', 'wav', '-']
            encodeCmd = ['lame', '--replaygain-accurate', '--vbr-new', '-b192', '-q0', '-V0', '-', targetPathAbs]
            _logger.debug( "Converting %d of %d: %s" % (i, totalCopies, relPath) )

            targetLeafDir = os.path.dirname( targetPathAbs )
            if not os.path.isdir( targetLeafDir ):
                os.makedirs( targetLeafDir )

            decodeProc = subprocess.Popen(decodeCmd, stdout=subprocess.PIPE)
            encodeProc = subprocess.Popen(encodeCmd, stdin=decodeProc.stdout)
            encodeProc.communicate();
    else:
        _logger.info( "No files to convert" )

def _copy( sourceDirAbs, relPaths, targetDirAbs ):
    totalCopies = len( relPaths )
    if totalCopies > 0:
        _logger.info( "Copying %d files" % totalCopies )
        i = 0
        for relPath in relativePaths:
            i += 1
            sourcePathAbs = os.path.join( sourceDirAbs, relPath )
            targetPathAbs = os.path.join( targetDirAbs, relPath )
            _logger.debug( "Copying %d of %d: %s" % (i, totalCopies, relPath) )
            
            targetLeafDir = os.path.dirname( targetPathAbs )
            if not os.path.isdir( targetLeafDir ):
                os.makedirs( targetLeafDir )
                    
            shutil.copyfile( sourcePathAbs, targetPathAbs )
            break;
    else:
        _logger.info( "No files to copy" )


def _delete( targetDirAbs, relativePaths ):
    for relPath in relativePaths:
        absPath = os.path.join( targetDirAbs, relPath )
        _logger.info( "Deleting: %s" % absPath )
        os.remove( absPath )
        

def _setupLogging( logFileAbs, isVerbose ):

    logFileAbs = os.path.expanduser(logFileAbs)
    logging.getLogger().setLevel( logging.DEBUG )

    fileHandler = logging.FileHandler( filename = logFileAbs, mode = 'w')
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
        _logger.info( "For verbose/debug output use '-b' or see log file: "
                      + logFileAbs )


class _Config:
    def __init__( self, logFileAbs ):
        self.jobConfigs = {}
        self.logFileAbs = logFileAbs

    def __str__( self ):
        strRep = 'jobs:\n'
        for jobName, jobConfig in self.jobConfigs.items():
            strRep += "  %s:\n" % jobName
            strRep += "    source: %s\n" % jobConfig.sourceDirAbs
            strRep += "    extensions to convert: %s\n" % jobConfig.extensionsToConvert
            strRep += "    extensions to copy: %s\n" % jobConfig.extensionsToCopy
            strRep += "    excluded patterns: %s\n" % jobConfig.excludePatterns
            strRep += "    target: %s\n" % jobConfig.targetDirAbs
            strRep += "    shell command: %s\n" % jobConfig.shellCmd
        return strRep
        
    class JobConfig:        
        def __init__( self, sourceDirAbs, extensionsToConvert, extensionsToCopy,
                      excludePatterns, targetDirAbs, shellCmd ):
            self.sourceDirAbs = sourceDirAbs
            self.extensionsToConvert = extensionsToConvert
            if extensionsToCopy == None:
                self.extensionsToCopy = []
            else:
                self.extensionsToCopy = extensionsToCopy
            self.excludePatterns = excludePatterns
            self.targetDirAbs = targetDirAbs
            self.shellCmd = shellCmd

def main(args):
    
    confFileAbs = _determineConfigFileAbs()
    config = _parseConfig( confFileAbs )
    _setupLogging( config.logFileAbs, isVerbose = True )
    print( config )
    jobConfig = config.jobConfigs['original_to_portable']
    i = 0

    allExtensions = jobConfig.extensionsToConvert.union( jobConfig.extensionsToCopy )
    sourcePaths = _all_file_paths( jobConfig.sourceDirAbs,
                                   allExtensions,
                                   jobConfig.excludePatterns )
    for sourceFile in sorted( sourcePaths ):
        i += 1
#        print sourceFile
        if i == 100:
            print sourceFile
    print i

    i = 0
    targetDirExtensions = jobConfig.extensionsToCopy.union(['mp3'])
    targetPaths = _all_file_paths( jobConfig.targetDirAbs,
                                   targetDirExtensions,
                                   jobConfig.excludePatterns )
    for sourceFile in targetPaths:
        i += 1
    print i

    sourceAdds, targetDeletes = _determine_adds_and_deletes( sourcePaths, targetPaths,
                                                             allExtensions, targetDirExtensions )
    print "adds: %d" % len( sourceAdds )
    print "dels: %d" % len( targetDeletes)

    if len( jobConfig.extensionsToCopy ) > 0:
        relPathsToCopy = _match_extensions( sourceAdds, jobConfig.extensionsToCopy )
        _copy( jobConfig.sourceDirAbs, relPathsToCopy, jobConfig.targetDirAbs )

    if len( jobConfig.extensionsToConvert ) > 0:
        relPathsToConvert = _match_extensions( sourceAdds, jobConfig.extensionsToConvert )
        _convertToMp3( jobConfig.sourceDirAbs, relPathsToConvert, jobConfig.extensionsToConvert, jobConfig.targetDirAbs )

    _delete( jobConfig.targetDirAbs, targetDeletes )

if __name__ == "__main__":
    main(sys.argv)
