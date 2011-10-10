#!/bin/bash

infile="$1"
outfile="${infile%.flac}.m4a"
ffmpeg -i "$infile" -acodec alac "$outfile"
MP4Box -inter 0 "$outfile"
panko import "$infile" "$outfile"