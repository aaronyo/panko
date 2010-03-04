import os
import sys
import stat
import fnmatch
import logging
import ConfigParser
import shutil
import logging
import meta.generic

_logger = logging.getLogger();

def _stripExtension( path ):
    return os.path.splitext( path )[0]
    
def matchExtensions( relativePaths, extensions ):
    patterns = set()
    for ext in extensions:
        patterns.add('*' + os.extsep + ext)

    matches = []
    for relPath in relativePaths:
        for pattern in patterns:
            if fnmatch.fnmatch(relPath, pattern):
                matches.append( relPath )
    return matches


def filterPaths( relativePaths, baseDirAbs, passConditionTemplate ):
    checkExt = False
    checkBitrate = False
    formatKwargs = {}
    if passConditionTemplate.find( "{extension}" ) != -1:
        checkExt = True
        formatKwargs["extension"] = "ext"
    if passConditionTemplate.find( "{bitrate}" ) != -1:
        checkBitrate = True
        formatKwargs["bitrate"] = "bitrate"

    passCondition = passConditionTemplate.format( **formatKwargs )

    passes = []
    rejects = []

    for relPath in relativePaths:
        if checkExt:
            ext = _stripExtension( relPath )
        if checkBitrate:
            pathAbs = os.path.join( baseDirAbs, relPath )
            audioFile = meta.generic.constructAudioFile( pathAbs )
            bitrate = int( audioFile.bitrate / 1000 )
        if eval ( passCondition ):
            passes.append( relPath )
        else:
            rejects.append( relPath )
        
    return passes, rejects

def findPaths(baseDirAbs, extensions=None, excludePatterns=None, returnRelPath=True):

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
                        if returnRelPath:
                            paths.add( os.path.relpath( absolutePath, baseDirAbs ) )
                        else:
                            paths.add( absolutePath )
                    break

    return paths

def convertPaths( sourceDir, relPaths, targetDirAbs, streamConverter, metaConverter ):

    streamConverter
    totalCopies = len( relPaths )
    i = 0
    streamConversionErrors = {}
    metaConversionErrors = {}
    for relPath in relPaths:
        i += 1
        _logger.debug( "Converting %d of %d: %s" % (i, totalCopies, relPath) )
        sourcePathAbs = os.path.join( sourceDir, relPath )
        relPathMinusExtension = _stripExtension( relPath )
        targetPathAbs = os.path.join( targetDirAbs, relPathMinusExtension + os.extsep + "mp3" )
        try:
            streamConverter.convert( sourcePathAbs, targetPathAbs )
            streamConversionError = None
        except Exception as e:
            streamConversionError = e
        try:
            metaConverter.convert( sourcePathAbs, targetPathAbs )
            metaConversionError = None
        except Exception as e:
            metaConversionError = e

        # We'll yield errors, instead of returning them all at the end, so that the caller
        # has control to stop processing due to errors
        yield streamConversionError, metaConversionError

def copyPaths( sourceDirAbs, relPaths, targetDirAbs ):
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

def deletePaths( targetDirAbs, relativePaths ):
    for relPath in relativePaths:
        absPath = os.path.join( targetDirAbs, relPath )
        _logger.debug( "Deleting: %s" % absPath )
        os.remove( absPath )
        

# Determine all new sources, updated sources and matchless targets so that we
# can identify the tasks necessary to bring the target collection up to date with the
# source collection.  File conversion is assumed, so extensions are ignored in
# processing the diff.
#
# The function assumes only one file exists per title exists (e.g. file paths differ
# by more than just extension).  If this is not the case for some title, the function
# will ensure that at least one copy of the title remains or is scheduled for the
# targets.
def extensionIgnorantDiff( sources, targets, sourceDirAbs, targetDirAbs ):

    def _hasBeenUpdated( sourcePath, targetPath, sourceDirAbs, targetDirAbs ):
        sourceModTime = os.stat( os.path.join(sourceDirAbs, sourcePath) )[stat.ST_MTIME]
        targetModTime = os.stat( os.path.join(targetDirAbs, targetPath) )[stat.ST_MTIME]
        return sourceModTime > targetModTime

    def _stripExtensions( filePaths ):
        stripped = []
        for path in filePaths:
            # leaves the '.' on the end so that file sort order doesn't change
            stripped.append( _stripExtension(path) + os.extsep )            
        return stripped

    sortedSources = sorted( sources )
    strippedSortedSources = _stripExtensions( sortedSources )

    sortedTargets = sorted( targets )
    strippedSortedTargets = _stripExtensions( sortedTargets )
    
    newSources = []
    updatedSources = []
    matchlessTargets = []
    numSources = len( strippedSortedSources ) 
    numTargets = len( strippedSortedTargets ) 
    sIdx = 0
    tIdx = 0
    targetMatched = False

    # Two pointers, one for the sources and one for the targets, are walked in tandem.  Since the
    # sources and targets have been sorted, we can diff the two lists in a single pass through
    # both lists.
    while not (sIdx == numSources and tIdx == numTargets):
        if sIdx == numSources:
            if not targetMatched:
                matchlessTargets.append( sortedTargets[tIdx] )
            tIdx += 1
            targetMatched = False
        elif tIdx == numTargets:
            newSources.append( sortedSources[sIdx] )
            sIdx += 1
        else:
            comparison = cmp( strippedSortedSources[sIdx], strippedSortedTargets[tIdx] )
            # This algorithm will not allow duplicate paths (with diff extenson, only) to remain in the target folder
            # The second path encountered will be indicated as matchless.
            if comparison == 0:
                # Indicate the match so we don't delete the target on the next loop
                targetMatched = True
                if _hasBeenUpdated( sortedSources[sIdx], sortedTargets[tIdx], sourceDirAbs, targetDirAbs ):
                    updatedSources.append( sortedSources[sIdx] )
                sIdx += 1
            elif comparison < 0:
                assert(not targetMatched)
                newSources.append( sortedSources[sIdx] )
                sIdx += 1
            elif comparison > 0:
                if not targetMatched:
                    matchlessTargets.append( sortedTargets[tIdx] )
                tIdx += 1
                targetMatched = False
    
    return newSources, updatedSources, matchlessTargets

def updateMeta( trackMeta, pathsAbs ):
    for pathAbs in pathsAbs:
        trackMeta.writeFile( pathAbs )
