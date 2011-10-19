import sys

def main():
    if len (sys.argv) > 1:
        sys.argv.pop(0)
        command = sys.argv[0]
        if command == 'import':
            import import_
            import_.main()
            sys.exit(0)
        elif command == 'info':
            import info
            info.main()
            sys.exit(0)
        elif command == 'write':
            import write
            write.main()
            sys.exit(0)
    
    # An appropriate ommand was not specified
    print 'usage: panko info|import'
    
if __name__ == '__main__':
    main()
        