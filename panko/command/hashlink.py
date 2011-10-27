import sys
import argparse
import os
import fnmatch
import re

from panko import audiofile

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('out_dir', metavar='OUT_DIR', type=str,
                         help='The directory that the hash link will be placed in')
    parser.add_argument('files', metavar='FILES', type=str, nargs='+',
                       help='the audio files that will be inspected')
    return parser.parse_args()
    
def main():
    args = parse_args()
    hashlinks = os.listdir(args.out_dir)
            
    for filename in args.files:
        md5val = audiofile.open(filename).audio_md5()
        _, ext = os.path.splitext(filename)
        matches = [os.path.join(args.out_dir, hl) for hl in hashlinks if fnmatch.fnmatch(hl, "%s*" % md5val)]
        if matches:
            already_linked = False
            for match in matches:
                 inode = os.stat(os.readlink(match)).st_ino
                 source_inode = os.stat(filename).st_ino
                 if inode == source_inode:
                     print "%s: File already linked: %s" % (filename, os.path.basename(match))
                     already_linked = True
                     
            if already_linked:
                continue
                
            matches = sorted([os.path.splitext(m)[0] for m in matches])
            last_dupe_match = re.match('.+dupe-(\d+)', matches[-1])
            if last_dupe_match:
                dupe_num = int(last_dupe_match.group(1)) + 1
            else:
                dupe_num = 1
            dupe_part = "-dupe-%02i" % dupe_num
        else:
            dupe_part = ""
        fname = md5val + dupe_part + ext
        link_target = os.path.join(args.out_dir, fname)
        os.symlink(filename, link_target)
        hashlinks.append(fname)
        
        
if __name__ == '__main__':
    main()