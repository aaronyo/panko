#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "usage: $0 INFILE BACKUP_DIR"
    exit 1
fi
infile="$1"
backup_base="$2"
backup_dir=${backup_base}/`dirname "$infile"`
if [ ! -d "$backup_dir" ]
    then mkdir -p "$backup_dir"
fi
outfile="${infile%.flac}.m4a"
ffmpeg -y -i "$infile" -acodec alac "$outfile"

# ffmpeg puts the metadata atom ('moov') at end of file.
# move it to the front so panko/mutagen can find it
MP4Box -inter 0 "$outfile"

panko import "$infile" "$outfile"
mv "${infile}" "${backup_base}/${infile}"