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
    parser.add_argument('files', metavar='FILES', type=str, nargs='*',
                       help='the audio files that will be inspected')
    parser.add_argument('-c', '--command',
                        help='echonest api command in form module.command',
                        default=None)
    parser.add_argument('-a', '--echo-args', nargs='*', type=str,
                        help='api args in form name:value',
                        default=None)
    return parser.parse_args()
    
    
def main():
    echonest.config_service()
    args = parse_args()
    if args.command == 'playlist.static':
        print "["
        for file_path in (args.files):
            try:
                af = audiofile.open(file_path)
                id = af.read_tags().get('echonest_id', None)
                songs_by_file = {}
                if id:
                    songs = []
                    for song in echonest.playlist.static(song_id=id, results=20, seed_catalog='CAMQJMD133B59A5B1C', type='catalog'):
                        songs.append( {'id':song.id,
                                       'title':song.title,
                                       'artist_name':song.artist_name,
                                       'artist_id':song.artist_id} )
                    print json.dumps({file_path:songs}, sort_keys=True)
                    print ","
            except Exception, e:
                sys.stderr.write(str(e))
        print "]"
    elif args.command == 'catalog.create':
        catalog = _get_or_create_catalog(args)
        print catalog.id
    elif args.command == 'catalog.update':
        catalog = _get_or_create_catalog(args)
        items = []
        for file_path in (args.files):
            try:
                af = audiofile.open(file_path)
                tags = af.read_tags()
                
                # API requires you to provide an id unique within the catalog
                item_id = hashlib.md5(os.path.abspath(file_path)).hexdigest()
                item = { 'song_id': tags['echonest_id'][0],
                         'release': tags.get('album_title', [None])[0],
                         'track_number': tags.get('track_number', [None])[0],
                         'disc_number': tags.get('disc_number', [None])[0],
                         'item_id': item_id }
                try:
                    int(item['track_number'])
                except:
                    item.pop('track_number')
                try:
                    int(item['disc_number'])
                except:
                    item.pop('disc_number')
                item = {k:v for k, v in item.items() if v}
                    
                items.append({'action':'update', 'item':item})
            except Exception, e:
                sys.stderr.write(str(e))
        print "submitting update request with %i items" % len(items)
        ticket_id = catalog.update(items)
        print "Ticket ID: %s" % ticket_id
    elif args.command == 'catalog.read':
        catalog = _get_or_create_catalog(args)
        print catalog.read_items()
    elif args.command == 'catalog.status':
        #FIXME: crazy brittle
        ticket_id = args.echo_args.pop()
        catalog = _get_or_create_catalog(args)
        print catalog.status(ticket_id)
    

def _get_or_create_catalog(args):
    echo_kwargs = {}
    echo_args = []
    for a in args.echo_args:
        if ':' in a:
            name, value = a.split(':'); echo_kwargs[name] = value
        else:
            echo_args.append(a)
    return echonest.catalog.Catalog(*echo_args, **echo_kwargs)
            
if __name__ == '__main__':
    main()
