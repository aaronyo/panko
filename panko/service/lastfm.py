from ..audiofile import albumart
import requests
import lxml.html
from lxml import etree
import ConfigParser
import pkg_resources


def make_service(api_key=None, base_url=None):
    config = ConfigParser.ConfigParser()
    config.read( pkg_resources.resource_filename(__name__, 'lastfm.ini') )
    api_key = api_key or config.get('web_service', 'api_key')
    base_url = base_url or config.get('web_service', 'base_url')
    return Service(api_key, base_url)
    
class Service(object):
    
    def __init__(self, api_key, base_url):
        self._api_key = api_key
        self._base_url = base_url
        self._cached_responses = {}
        

    def _album_info_query_params(self, tags):
        return { 'method': 'album.getinfo',
                 'api_key': self._api_key,
                 'artist': tags['album_artist'][0].encode('utf-8'),
                 'album': tags['album_title'][0].encode('utf-8') }

    @staticmethod
    def _extract_image_url(xml_str):
        dom = lxml.html.fromstring( xml_str.encode('utf-8') )
        return dom.xpath("//image[@size='mega']")[0].text

    def get_cover_art_url(self, tags):
        #FIXME: cache should not grow indefinitely
        params = self._album_info_query_params(tags)
        key = str(sorted(params.items()))
        if key not in self._cached_responses:
            self._cached_responses[key] = requests.get( self._base_url,
                                                   params=params )
        response = self._cached_responses[key]
        return self._extract_image_url( response.content )

    def get_cover_art(self, tags):
        image_url = self.get_cover_art_url(tags)
        return albumart.load_url(image_url)
