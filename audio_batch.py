#!/usr/bin/env python
import os
import sys
import fnmatch
import logging
import optparse
import subprocess
import ConfigParser

def _buildCmdLineParser():
    parser = OptionParser.OptionParser()

    return parser

def _determineConfigFileAbs():
    homePath = os.path.expanduser('~')
    return os.path.join(homePath, '.audio_batch/audio_batch.ini')

def _parseConfig( confFileAbs ):

    def _parseJob( confParser, jobName ):
        sourceFileExtensions = set( confParser.get( jobName, "source_file_extensions" ).split( ';' ) )
        if confParser.has_option( jobName, "source_file_excludes" ):
            sourceExcludePatterns = set( confParser.get( jobName, "source_file_excludes" ).split( ';' ) )
        else:
            souceExcludePatterns = None
        jobConfig = _Config.JobConfig( confParser.get( jobName, "source_path" ),
                                       sourceFileExtensions,
                                       sourceExcludePatterns,
                                       confParser.get( jobName, "target_path" ),
                                       confParser.get( jobName, "shell_cmd" ) )
        return jobConfig

    config = _Config()
    confParser = ConfigParser.ConfigParser()
    confParser.read( confFileAbs )
    jobNames = confParser.options( "jobs" )
    for jobName in jobNames:
        config.jobConfigs[jobName] = _parseJob( confParser, jobName )

    return config

def _all_file_paths(baseDirAbs, extensions=None, excludePatterns=None):

    def _shouldExclude( path, excludePatterns ):
        if excludePatterns == None:
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

def _strip_extensions( filePaths, extensions ):
    stripped = set()
    for path in filePaths:
        for ext in extensions:
            fileSuffix = os.extsep + ext
            if path.endswith( fileSuffix ):
                stripped.add( path[: -len(fileSuffix) ] )
    return stripped


def _diff_paths( sources, targets, sourceExtensions, targetExtension, ignoreExtensions=True ):
    if ignoreExtensions:
        if sourceExtensions == None or targetExtension == None:
            raise Exception("Must supply extensions to ignore")

        sources = _strip_extensions( sources, sourceExtensions )
        targets = _strip_extensions( targets, [targetExtension] )
    
    return sources.difference( targets )


def _convert( sourceDir, targetDir, paths, audioFormat ):
    pass

class _Config:
    def __init__( self ):
        self.jobConfigs = {}

    def __str__( self ):
        strRep = 'jobs:\n'
        for jobName, jobConfig in self.jobConfigs.items():
            strRep += "  %s:\n" % jobName
            strRep += "    source: %s\n" % jobConfig.sourcePathAbs
            strRep += "    source included extensions: %s\n" % jobConfig.sourceFileExtensions
            strRep += "    source excluded patterns: %s\n" % jobConfig.sourceExcludePatterns
            strRep += "    target: %s\n" % jobConfig.targetPathAbs
            strRep += "    shell command: %s\n" % jobConfig.shellCmd
        return strRep
        
    class JobConfig:        
        def __init__( self, sourcePathAbs, sourceFileExtensions, sourceExcludePatterns, targetPathAbs, shellCmd ):
            self.sourcePathAbs = sourcePathAbs
            self.sourceFileExtensions = sourceFileExtensions
            self.sourceExcludePatterns = sourceExcludePatterns
            self.targetPathAbs = targetPathAbs
            self.shellCmd = shellCmd

def main(args):
    
    confFileAbs = _determineConfigFileAbs()
    config = _parseConfig( confFileAbs )
    print( config )
    jobConfig = config.jobConfigs['original_to_portable']
    i = 0

    sourcePaths = _all_file_paths( jobConfig.sourcePathAbs,
                                   jobConfig.sourceFileExtensions,
                                   jobConfig.sourceExcludePatterns )
    for sourceFile in sourcePaths:
        i += 1
        print sourceFile
#        if i == 100:
#            print sourceFile
    print i

    targetPaths = _all_file_paths( jobConfig.targetPathAbs )
    for sourceFile in targetPaths:
        i += 1
    print i

    diff = _diff_paths( sourcePaths, targetPaths, jobConfig.sourceFileExtensions, 'mp3' )
    print len(diff)
    

if __name__ == "__main__":
    main(sys.argv)
