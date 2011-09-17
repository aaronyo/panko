import sys
import argparse
from audiobatch import audiofile

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=unicode, nargs='+',
                       help='the audio files that will be inspected')
    return parser.parse_args()
    

def main():
    args = parse_args()
    for file_path in args.files:
        af = audiofile.load(file_path)
        print af.pretty()

if __name__ == '__main__':
    main()