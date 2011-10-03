import sys
import argparse
import csv
import sys
import StringIO

from audiobatch import audiofile
from audiobatch import util

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

def decode_all(values):
    decoded = []
    for v in values:
        if isinstance(v, str):
            decoded.append( unicode(v.encode('string-escape')) )
        elif isinstance(v, unicode):
            decoded.append(v)
        else:
            decoded.append(unicode(str(v), 'utf-8'))
    return decoded
            
        

def format_rows(rows):
    def format_value(value):
        value = util.seqify(value)
        unicoded = decode_all(value)
        strio = StringIO.StringIO()
        writer = csv.writer(strio)
        writer.writerow(unicoded)
        return strio.getvalue()[:-1]
    
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