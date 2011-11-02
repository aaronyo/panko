import sys
import argparse
import StringIO

from panko import audiofile
from panko import albumart
from panko.service import lastfm
from panko.service import echonest

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                         help='the audio files that will be inspected')
    parser.add_argument('-c', '--cover', help='discover url for cover art',
                        default=False, action='store_true')
    parser.add_argument('-e', '--echonest-id', help='discover echonest id for this file',
                        default=False, action='store_true')
    parser.add_argument('-i', '--if-needed',
                        help='only discover if no value is already present in the file',
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
            if args.cover \
            and (not args.if_needed or not target_file.has_embedded_cover()):
                target_file = audiofile.open(filepath)
                tags = target_file.read_tags()
                lfm_service = lastfm.make_service()
                cover_url = lfm_service.get_cover_art_url(tags)
                if args.update:
                    target_file.embed_cover( albumart.load_url(cover_url),
                                             format=args.cover_format )
                    print '%s: updated with cover %s' % (filepath, cover_url)
                else:
                    print cover_url
            elif args.echonest_id \
            and (not args.if_needed or 'echonest_id' not in target_file.tags()):
                en_service = echonest.make_service()
#                echonest_id = en_service.get_echonest_id(filepath)
                echonest_id = en_service.song.identify(filepath)

                if args.update:
                    target_file.write_tags({'echonest_id':echonest_id})
                    print '%s: updated with id %s' % (filepath, cover_url)
                else:
                    print echonest_id
            else:
                print '%s: nothing to do' % filepath
        except Exception as e:
            print 'Trouble with file %s: %s' % (filepath, e)

if __name__ == '__main__':
    main()