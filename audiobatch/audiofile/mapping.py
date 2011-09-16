# Notes about mappings:
#   To indicate multiple possible names for a format's tag, separate
#   the names with commas.  The first name will be used for writing this
#   format.
#
#   Some audiobatch names, like track_number and track_total, may map to 
#   information stored in a single format tag.  Array index notation is used
#   to indicate which part of the format's tag is desired.  Note that the actual
#   parsing and construction of the compound tag is hard wired in the code.
#   MP4 and MP3 are expected to separate elements with a "/" and always use the
#   same order.
#
#   A '*' anywhere in the table indicates that a corresponding footnote exists at
#   the bottom of the file.


DEFAULT_MAPPING=\
r"""
album_titles:
    type: unicode[]
    mp4: \xa9alb
    mp3: TALB   
    flac: albumtitle

album_artists:
    type: unicode[]
    mp4: aART
    mp3: TPE2
    flac: albumartist

album_release_date:
    type: FlexDateTime
    mp4: \xa9day
    mp3: TDRC
    flac: date

artists:
    type: unicode[]
    mp4: \xa9alb
    mp3: TPE1
    flac: artist

composers:
    type: unicode[]
    mp4: \xa9wrt
    mp3: TCOM
    flac: composer

titles:
    type: unicode[]
    mp4: \xa9nam
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
"""

# genres*						unicode[]			\xa9gen		TCON   		genre
# groupings						unicode[]       	\xa9grp		TIT1
# comment 						unicode				\xa9cmt		COMM::'eng'
# bpm								int					tmpo		TBPM
# lyrics							unicode				\xa9lyr		USLT::'eng'
# copyright						unicode				cprt		
# encoding_tool					unicode				\xa9too
# encoded_by						unicode				\xa9enc
# purchase_date					FlexDateTime		purd
# content_rating					int					rtng
# is_compilation					bool				cpil
# sort_title						unicode				sonm		TSOT
# sort_artist						unicode				soar		TSOA
# sort_album_artist				unicode				soaa		TSO2
# sort_album_title				unicode				soal		TSOA
# sort_composer					unicode				soco		TSOC
# itunes_purchase_accont			unicode				apID
# itunes_purchase_account_type	int					akID
# itunes_purchase_catalog_number	int					cnID
# itunes_purchase_country_code	int					sfID
# isrc							str					----:com.apple.iTunes:ISRC
# itunes_cddb_id					str					----:com.apple.iTunes:iTunes_CDDB_1
# itunes_cddb_track_number		int					----:com.apple.iTunes:iTunes_CDDB_TrackNumber
# 
# 
# *id3
#   Mutagen supports all versions of id3, from 1 up to 2.4, and attempts to write tags in the
#   same version as what is found in the file.
# 
# *genres
#   Mutagen seems to do a good job of converting any numeric id3v1 style genre fields
#   to the freeform string version of the genre.  It also generally only writes the freeform
#   version.  This seems to be the trend -- ditching the numeric genre -- so I don't see
#   a good reason to support reading or setting it.  Thank you, mutagen.
