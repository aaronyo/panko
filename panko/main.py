import sys

def main():
    if len (sys.argv) > 1:
        sys.argv.pop(0)
        command = sys.argv[0]
        if command == 'import':
            from .command import import_
            import_.main()
            sys.exit(0)
        elif command == 'info':
            from .command import info
            info.main()
            sys.exit(0)
        elif command == 'update':
            from .command import update
            update.main()
            sys.exit(0)
        elif command == 'discover':
            from .command import discover
            discover.main()
            sys.exit(0)
        elif command == 'hashlink':
            from .command import hashlink
            hashlink.main()
            sys.exit(0)
        elif command == 'filter':
            from .command import filter
            filter.main()
            sys.exit(0)
        elif command == 'echonest':
            from .command import echonest
            echonest.main()
            sys.exit(0)
    
    # An appropriate ommand was not specified
    print 'usage: panko info|update|discover|import|hashlink'
    
if __name__ == '__main__':
    main()
        