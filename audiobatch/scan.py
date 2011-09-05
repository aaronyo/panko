def scan( self,
          base_dir_abs,
          extensions = None,
          exclude_patterns = None,
          return_rel_path = True ):
    ''' Return paths of audio files found beneath the designated base directory '''

    paths = set()
    for path, _, files in os.walk(base_dir_abs):
        for name in files:
            patterns = []
            if extensions == None:
                patterns.append('*')
            else:
                for ext in extensions:
                    patterns.append('*' + os.extsep + ext)
            for pattern in patterns:
                if fnmatch.fnmatch(name, pattern):
                    absolute_path = os.path.join(path, name)
                    if not TrackRepository._should_exclude(
                        absolute_path,
                        exclude_patterns ):
                        if return_rel_path:
                            paths.add( os.path.relpath( absolute_path,
                                                        base_dir_abs ) )
                        else:
                            paths.add( absolute_path )
                    break

    return paths
