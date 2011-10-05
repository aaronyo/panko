import sys
import argparse
import StringIO

from audiobatch import audiofile

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('source_file', metavar='SOURCE_FILE', type=str,
                       help='the audio files that will be inspected')
    parser.add_argument('target_file', metavar='TARGET_FILE', type=str,
                         help='the audio files that will be inspected')
    return parser.parse_args()
    
def main():
    args = parse_args()
    source_file = audiofile.open(args.source_file)
    target_file = audiofile.open(args.target_file)
    target_file.write_tags(source_file.read_tags())
    cover_art = source_file.extract_cover() or source_file.folder_cover()
    if cover_art:
        target_file.embed_cover(cover_art)
        
if __name__ == '__main__':
    main()