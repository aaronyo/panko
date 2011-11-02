from .. import albumart
import requests
import lxml.html
from lxml import etree
import ConfigParser
import pkg_resources
import subprocess

def make_service( api_key=None,
                  base_url=None,
                  codegen_cmd=None,
                  sample_start=None,
                  sample_duration=None):
    config = ConfigParser.ConfigParser()
    config.read( pkg_resources.resource_filename(__name__, 'echonest.ini') )
    api_key = api_key or config.get('web_service', 'api_key')
    base_url = base_url or config.get('web_service', 'base_url')
    codegen_cmd = codegen_cmd or config.get('enmfp_code', 'shell_command')
    sample_start = sample_duration or int( config.get( 'enmfp_code',
                                                       'sample_start') )
    sample_duration = sample_duration or int( config.get( 'enmfp_code',
                                                          'sample_duration') )
    return Service(api_key, base_url, codegen_cmd, sample_start, sample_duration)
    
class Service(object):
    
    def __init__(self, api_key, base_url, codegen_cmd, sample_start, sample_duration):
        self._api_key = api_key
        self._base_url = base_url
        self._codegen_cmd = codegen_cmd
        # ensure duration is an int
        self._sample_start = int( sample_start )
        self._sample_duration = int( sample_duration )
        self._cached_responses = {}
    
    def extract_query_params(self, filepath):
        cmd_seq = [self._codegen_cmd, filepath,
                   str(self._sample_start), str(self._sample_duration)]
        proc = subprocess.Popen(cmd_seq, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if stderr:
            #FIXME: use proper excepion
            raise Exception(stderr)
        result = eval(stdout)[0]
        if 'error' in result:
            #FIXME: use proper excepion
            raise Exception(result['error'])
        return result
    
    def get_echonest_id(self, filepath):
        return self.extract_query_params(filepath)