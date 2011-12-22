import sys
import argparse
import pprint
import json
import hashlib
import os

from panko import audiofile
from panko import util
from panko.service import echonest

def parse_args():
    parser = argparse.ArgumentParser(description='Display an audio files meta data.')
    parser.add_argument('-a', '--artist', type=str, default=None)
    parser.add_argument('-t', '--title', type=str, default=None)
    return parser.parse_args()
    
def main():
    echonest.config_service()
    args = parse_args()
    recommendations = recommend(args.artist, args.title)
    print json.dumps(recommendations, sort_keys=True)
        
def recommend(artist, title):
        echonest.config_service()
        matches = echonest.song.search(artist=artist, title=title, )
        if not matches:
            return []
        echonest_id = matches[0].id
        songs = []
        for song in echonest.playlist.static(song_id=echonest_id, results=20, seed_catalog='CAMQJMD133B59A5B1C', type='catalog'):
            songs.append( {'id':song.id,
                           'title':song.title,
                           'artist':song.artist_name,
                           'artist_id':song.artist_id} )
        return songs

if __name__ == '__main__':
    main()
