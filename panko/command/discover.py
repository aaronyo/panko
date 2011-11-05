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
            target_file = audiofile.open(filepath)
            tags = target_file.read_tags()
            if args.cover \
            and (not args.if_needed or not target_file.has_embedded_cover()):
                lfm_service = lastfm.make_service()
                cover_url = lfm_service.get_cover_art_url(tags)
                if args.update:
                    target_file.embed_cover( albumart.load_url(cover_url),
                                             format=args.cover_format )
                    print '%s: updated with cover %s' % (filepath, cover_url)
                else:
                    print cover_url
            elif args.echonest_id \
            and (not args.if_needed or 'echonest_id' not in target_file.read_tags()):
                echonest.config_service()
                echonest_id = echonest.song.identify(filepath,
                                                     codegen_start = echonest.codegen_start,
                                                     codegen_duration = echonest.codegen_duration)[0].id

                if args.update:
                    target_file.write_tags({'echonest_id':echonest_id})
                    print '%s: updated with id %s' % (filepath, echonest_id)
                else:
                    print echonest_id
            else:
                print '%s: nothing to do' % filepath
        except Exception as e:
            print 'Trouble with file %s: %s' % (filepath, e)
        sys.stdout.flush()

if __name__ == '__main__':
    main()