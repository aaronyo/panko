import sys
import argparse

from panko import audiofile
from panko import util

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                       help='the audio files that will be inspected')
    parser.add_argument('-t', '--tags',
                        help='comma separated list of common tag names',
                        default=None)
    parser.add_argument('-0', '--print0',
                        help='separate results with an ascii null; useful with "xargs -0"',
                        default=False, action='store_true')
    return parser.parse_args()
    
    
def main():
    args = parse_args()
    if args.print0:
        delim = '\x00'
    else:
        delim = '\n'
    for file_path in args.files:
        af = audiofile.open(file_path)
        if args.tags:
            tags = args.tags.split(",")
            results = {k: v for k, v in af.read_tags().items() if k in tags}
            if results:
                sys.stdout.write(file_path + delim)
                

if __name__ == '__main__':
    main()
