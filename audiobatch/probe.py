import sys
import argparse
import csv
import StringIO

from audiobatch import audiofile
from audiobatch import util

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                       help='the audio files that will be inspected')
    parser.add_argument('-r','--raw', action='store_true', default=False)
    return parser.parse_args()
    
def main():
    args = parse_args()
    for file_path in args.files:
        af = audiofile.open(file_path)
        print
        print "Tags:"
        print formatted_rows( af.read_extended_tags(keep_unknown=True), args.raw )
        print "Cover Art:"
        if af.has_folder_cover:
            cover = af.folder_cover()
            print "Folder Image: path='%s', type='%s', size=%s," % (af.folder_cover_path, cover.format, len(cover.bytes))
        if af.has_embedded_cover:
            cover = af.extract_cover()
            print "Embedded Image: location='%s', type='%s', size=%s, " % (af.embedded_cover_key(), cover.format, len(cover.bytes))
        print    
        

def decode_all(values):
    decoded = []
    for v in values:
        # Any data must support decoding to unicode
        decoded.append( unicode(v).encode('utf-8') )
    return decoded
            
        

def formatted_rows(rows, raw=False):
    def format_value(value):
        if value:
            value = util.seqify(value)
            unicoded = decode_all(value)
            strio = StringIO.StringIO()
            writer = csv.writer(strio)
            writer.writerow(unicoded)
            return unicode(strio.getvalue()[:-2], 'utf-8')
    def format_data(data):
        return data.__repr__()

    frmt_rows = [ (n or '(unmapped)', format_value(v) or '(not parsed)', unicode(l), format_data(d))
                  for n, v, l, d in rows if n or raw]
    lengths = [(len(n), len(v), len(l), len(d)) for n, v, l, d in frmt_rows]
    col_lengths = zip(*lengths)
    pad = [ max(l)+1 for l in col_lengths ]
    result = u""
    for row in frmt_rows:
        result += u"%-*s | %-*s"
        result_vars = [pad[0], row[0], pad[1], row[1]]
        if raw:
            result += " | %-*s | %s"
            result_vars.extend([pad[2], row[2], row[3]])
        result += "\n"
        result = result % tuple(result_vars)
    return result

if __name__ == '__main__':
    main()