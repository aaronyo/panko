# config format
#   To indicate multiple possible names for a format's tag, use a YAML list
#   The first name will be used by default when writing.
#
#   Some audiobatch tags, like track_number and track_total, may map to 
#   information stored in a single file tag, or a compound tag.  [] notation
#   is used to indicate which part of the file's tag is desired.  The actual
#   parsing and construction of the compound tag is hard wired in the code.
#   MP4 and MP3 are expected to separate elements with a "/".
#
#   A '*' anywhere in the table indicates that a corresponding footnote exists at
#   the bottom of the file.
#
# genres
#   Mutagen seems to do a good job of converting any numeric id3v1 style genre fields
#   to the freeform string version of the genre.  It also generally only writes the freeform
#   version.  This seems to be the trend -- ditching the numeric genre -- so I don't see
#   a good reason to support reading or setting it.
#
# not yet handled:
#   many id's, like musicbrainz id's and cddb id's... e.g., mp4 UFID tag... not sure when that
#   tag is used, vs. comment tags for id's, etc.
#
#



DEFAULT_MAP=\
"""
album_title:
    type: unicode[]
    mp4: (c)alb
    mp3: TALB   
    flac: [album, albumtitle]

album_artist:
    type: unicode[]
    mp4: aART
    mp3: TPE2
    flac: albumartist

album_release_date:
    type: FlexDateTime
    mp4: (c)day
    mp3: TDRC
    flac: date

artist:
    type: unicode[]
    mp4: (c)ART
    mp3: TPE1
    flac: artist

composer:
    type: unicode[]
    mp4: (c)wrt
    mp3: TCOM
    flac: composer

title:
    type: unicode[]
    mp4: (c)nam
    mp3: TIT2
    flac: title

track_number:
    type: int
    mp4: trkn[0]
    mp3: TRCK[0]
    flac: tracknumber
    
track_total:
    type: int
    mp4: trkn[1]
    mp3: TRCK[1]
    flac: [tracktotal, totaltracks]

disc_number:
    type: int
    mp4: disk[0]
    mp3: TPOS[0]
    flac: discnumber

disc_total:
    type: int
    mp4: disk[1]
    mp3: TPOS[1]
    flac: [disctotal, totaldiscs]

genre:
    type: unicode[]
    mp4: (c)gen
    mp3: TCON
    flac: genre

grouping:
    type: unicode[]
    mp4: (c)grp
    mp3: TIT1

comment:
    type: unicode
    mp4: (c)cmt
    mp3: COMM::'eng'
    
bpm:
    type: int
    mp4: tmpo
    mp3: TBPM

lyrics:
    type: unicode
    mp4: (c)lyr
    mp3: USLT::'eng'

copyright:
    type: unicode
    mp4: cprt

encoding_tool:
    type: unicode
    mp4: (c)too
    mp3: TENC
    
encoded_by:
    type: unicode
    mp4: (c)9enc

purchase_date:
    type: FlexDateTime
    mp4: purd

content_rating:
    type: int
    mp4: rtng

is_compilation:
    type: bool
    mp4: cpil
    mp3: TCMP

sort_title:
    type: unicode
    mp4: sonm
    mp3: TSOT

sort_artist:
    type: unicode
    mp4: soar
    mp3: TSOP

sort_album_artist:
    type: unicode
    mp4: soaa
    mp3: TSO2

sort_album_title:
    type: unicode
    mp4: soal
    mp3: TSOA

sort_composer:
    type: unicode
    mp4: soco
    mp3: TSOC

itunes_purchase_accont:
    type: unicode
    mp4: apID
    
itunes_purchase_account_type:
    type: int
    mp4: akID

itunes_purchase_catalog_number:
    type: int
    mp4: cnID
    
itunes_purchase_country_code:
    type: int
    mp4: sfID

isrc:
    type: str
    mp4: "----:com.apple.iTunes:ISRC"
    mp3: TSRC
    flac: isrc

itunes_cddb_id:
    type: str
    mp4: "----:com.apple.iTunes:iTunes_CDDB_1"
    mp3: "COMM:iTunes_CDDB_1:'eng'"

itunes_cddb_track_number:
    type: int
    mp4: "----:com.apple.iTunes:iTunes_CDDB_TrackNumber"
    mp3: "COMM:iTunes_CDDB_TrackNumber:'eng'"
"""

