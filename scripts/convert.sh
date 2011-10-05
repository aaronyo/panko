#!/bin/bash

infile="$1"
outfile="${infile%.flac}.m4a"
outfilecopy="${infile%.flac}_copy.m4a"
ffmpeg -i "$infile" -acodec alac "$outfile"
MP4Box -inter 0 "$outfile"
cp "$outfile" "$outfilecopy"
python ~/works/code/audiobatch/audiobatch/import.py "$infile" "$outfile"