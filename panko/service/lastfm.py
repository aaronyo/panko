from ..audiofile import albumart
import urllib
import urlparse
import urllib2
from lxml import etree

_NETLOC = 'ws.audioscrobbler.com'
_PATH = '/2.0/'
_API_KEY='cf7983d893669afcac2431cd699ae22d'

def _build_album_info_query(tags):
    query_items = {'method': 'album.getinfo',
                   'api_key': _API_KEY,
                   'artist': tags['album_artist'][0].encode('utf-8'),
                   'album': tags['album_title'][0].encode('utf-8')}
    return urllib.urlencode(query_items)

def _parse_image_url(xml_str):
    dom = etree.fromstring( xml_str )
    return dom.xpath("//image[@size='mega']")[0].text

def get_cover_art_url(tags):
    url_parts = urlparse.ParseResult(
            scheme='http', netloc=_NETLOC, path=_PATH,
            query=_build_album_info_query(tags),
            params='', fragment='')
    url = urlparse.urlunparse(url_parts)
    return _parse_image_url( urllib2.urlopen(url).read() )

def get_cover_art(tags):
    image_url = get_cover_art_url(tags)
    return albumart.load_url(image_url)
