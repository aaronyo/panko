import sys

if __name__ == '__main__':
    if len (sys.argv) < 2:
        command = sys.argv[1]
        if command == 'import':
            import import_
            import_.main()
            sys.exit(0)
        elif command == 'probe':
            import probe
            probe.main()
            sys.exit(0)
    
    # An appropriate ommand was not specified
    print 'usage: panko info|import'
        