import sys
import argparse
import csv
import StringIO

from panko import audiofile
from panko import util

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                       help='the audio files that will be inspected')
    parser.add_argument('-r','--raw', action='store_true', default=False)
    parser.add_argument('-c', '--cover', help='display the cover art',
                        default=False, action='store_true')
    return parser.parse_args()
    
    
def main():
    args = parse_args()
    for file_path in args.files:
        af = audiofile.open(file_path)
        print
        print "Tags:"
        print formatted_rows( af.read_extended_tags(keep_unknown=True), args.raw )
        print "Cover Art:"
        folder, embedded = af.folder_cover(), af.extract_cover()
        if folder:
            location = "  Folder Image: path='%s', " % af.folder_cover_path()
            print location + art_details(folder)            
        if embedded:
            location =  "  Embedded Image: key='%s', " % af.embedded_cover_key()
            print location + art_details(embedded)
        if not (folder or embedded):
            print 'None found'
        print
        if args.cover:
            af.extract_cover().to_pil_image().show()    
        
        
def art_details(art):
    dim = "x".join( map(str, art.dimensions()) )
    return "type='%s', size=%s, dimensions=%s" % \
           (art.format, len(art.bytes), dim)
    
    
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
        result += u"  %-*s | %-*s"
        result_vars = [pad[0], row[0], pad[1], row[1]]
        if raw:
            result += " | %-*s | %s"
            result_vars.extend([pad[2], row[2], row[3]])
        result += "\n"
        result = result % tuple(result_vars)
    return result

if __name__ == '__main__':
    main()