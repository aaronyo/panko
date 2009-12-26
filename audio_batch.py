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
        sourceFilePatterns = confParser.get( jobName, "source_file_patterns" ).split( ';' )
        jobConfig = _Config.JobConfig( confParser.get( jobName, "source_path" ),
                                       sourceFilePatterns,
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

def _all_file_paths(baseDirAbs, patterns):
    for path, subdirs, files in os.walk(baseDirAbs):
        for name in files:
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    absolutePath = os.path.join(path, name)
                    yield os.path.relpath( absolutePath, baseDirAbs )
                    break


def _diff_paths( source, target, ignoreExtensions=True ):
    pass

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
            strRep += "    source patterns: %s\n" % jobConfig.sourceFilePatterns
            strRep += "    target: %s\n" % jobConfig.targetPathAbs
            strRep += "    shell command: %s\n" % jobConfig.shellCmd
        return strRep
        
    class JobConfig:        
        def __init__( self, sourcePathAbs, sourceFilePatterns, targetPathAbs, shellCmd ):
            self.sourcePathAbs = sourcePathAbs
            self.sourceFilePatterns = sourceFilePatterns
            self.targetPathAbs = targetPathAbs
            self.shellCmd = shellCmd

def main(args):
    
    confFileAbs = _determineConfigFileAbs()
    config = _parseConfig( confFileAbs )
    print( config )
    jobConfig = config.jobConfigs['original_to_portable']
    i = 0
    for sourceFile in _all_file_paths( jobConfig.sourcePathAbs, jobConfig.sourceFilePatterns ):
        i += 1
        if i == 100:
            print sourceFile
    print i
    for sourceFile in _all_file_paths( jobConfig.targetPathAbs, jobConfig.sourceFilePatterns ):
        i += 1
    print i

    

if __name__ == "__main__":
    main(sys.argv)
