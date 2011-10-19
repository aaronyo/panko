from .. import albumart
import requests
import lxml.html
from lxml import etree

_BASE_URL = 'http://ws.audioscrobbler.com/2.0/'
_API_KEY='cf7983d893669afcac2431cd699ae22d'

_cached_responses = {}

def _album_info_query_params(tags):
    return {'method': 'album.getinfo',
            'api_key': _API_KEY,
            'artist': tags['album_artist'][0].encode('utf-8'),
            'album': tags['album_title'][0].encode('utf-8')}

def _parse_image_url(xml_str):
    dom = lxml.html.fromstring( xml_str.encode('utf-8') )
    return dom.xpath("//image[@size='mega']")[0].text

def get_cover_art_url(tags):
    global _cached_responses
    #FIXME: cache should not grow indefinitely
    params = _album_info_query_params(tags)
    key = str(sorted(params.items()))
    if key not in _cached_responses:
        _cached_responses[key] = requests.get( _BASE_URL, params=params )
    response = _cached_responses[key]
    return _parse_image_url( response.content )

def get_cover_art(tags):
    image_url = get_cover_art_url(tags)
    return albumart.load_url(image_url)
