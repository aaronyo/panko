import sys
import argparse
import StringIO

from panko import audiofile
from panko import albumart
from panko.service import lastfm

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                         help='the audio files that will be inspected')
    parser.add_argument('-c', '--cover', help='discover url for cover art',
                        default=False, action='store_true')
    parser.add_argument('-u', '--update',
                        help='update the target file(s) with the discovered info',
                        default=False, action='store_true')
    parser.add_argument('-f', '--cover-format', type=str, help='file or url for cover art',
                        default=None)
    return parser.parse_args()
    
def main():
    args = parse_args()
    for filepath in args.files:
        try:
            target_file = audiofile.open(filepath)
            tags = target_file.read_tags()
            if args.cover:
                cover_url = lastfm.get_cover_art_url(tags)
                if args.update:
                    target_file.embed_cover( albumart.load_url(cover_url),
                                             format=args.cover_format )
                    print 'Updated file "%s" with cover "%s"' % (filepath, cover_url)
                else:
                    print cover_url
        except Exception as e:
            print 'Trouble with file %s: %s' % (filepath, e)

if __name__ == '__main__':
    main()