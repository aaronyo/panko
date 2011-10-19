import sys
import argparse
import StringIO

from panko import audiofile
from panko.audiofile import albumart

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                         help='the audio files that will be inspected')
    parser.add_argument('-c', '--cover', type=str, help='file or url for cover art',
                        default=None)
    parser.add_argument('-f', '--cover-format', type=str, help='file or url for cover art',
                        default=None)
    return parser.parse_args()
    
def main():
    args = parse_args()
    art = None
    if args.cover:
        if args.cover.startswith('http://') or args.cover.startswith('https://'):
            art = albumart.load_url(args.cover)
        else:
            art = albumart.load(args.cover)
    for filepath in args.files:
        target_file = audiofile.open(filepath)
        if art:
            target_file.embed_cover(art, format=args.cover_format)
        
if __name__ == '__main__':
    main()