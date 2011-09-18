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
        print format_rows( af.rows() )

def format_rows(rows):
    def format_value(value):
        if hasattr(value, '__iter__'):
            return u", ".join([format(v) for v in value])
        elif isinstance(value, basestring):
            return u'"%s"' % value
        else:
            return unicode(value)
    
    frmt_rows = [ (n or '(unknown)', str(l), format_value(v))
                  for n, l, v in rows ]
    lengths = [(len(n), len(l), len(v)) for n, l, v in frmt_rows]
    col_lengths = zip(*lengths)
    pad = [ max(l)+1 for l in col_lengths ]
    result = u""
    for row in frmt_rows:
        result += u"%-*s| %-*s| %s\n" \
            % (pad[0], row[0], pad[1], row[1], row[2])
    return result

if __name__ == '__main__':
    main()