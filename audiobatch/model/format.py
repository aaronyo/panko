FLAC_STREAM = "flac"
MP3_STREAM = "mp3"
ALAC_STREAM = "alac"
AAC_STREAM = "aac"
WAV_STREAM = "wav"

FLAC_CONTAINER = "flac"
MP3_CONTAINER = "mp3"
MP4_CONTAINER = "mp4"
WAV_CONTAINER = "wav"

# default container type used for a given stream type
_STREAM_TO_CONTAINER = {
    FLAC_STREAM : FLAC_CONTAINER,
    MP3_STREAM  : MP3_CONTAINER,
    ALAC_STREAM : MP4_CONTAINER,
    AAC_STREAM  : MP4_CONTAINER,
    WAV_STREAM  : WAV_CONTAINER
}

# default extension used for a given container type
_CONTAINER_TO_EXT = {
    FLAC_CONTAINER : ["flac"],
    MP3_CONTAINER  : ["mp3"],
    MP4_CONTAINER  : ["m4a", "mp4"],
    WAV_CONTAINER  : ["wav"],
}

def container_to_ext( container ):
    return _CONTAINER_TO_EXT[ container ][0]

def stream_to_ext( stream ):
    return container_to_ext( _STREAM_TO_CONTAINER[ stream ] )

