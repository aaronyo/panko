import ConfigParser
import pkg_resources
import pyechonest
from pyechonest import *


codegen_start = None
codegen_duration = None

def config_service( api_key=None,
                    base_url=None,
                    codegen_cmd=None,
                    sample_start=None,
                    sample_duration=None):
    config = ConfigParser.ConfigParser()
    config.read( pkg_resources.resource_filename(__name__, 'echonest.ini') )
    pyechonest.config.ECHO_NEST_API_KEY = api_key or config.get('web_service', 'api_key')
    base_url = base_url or config.get('web_service', 'base_url')
    pyechonest.config.CODEGEN_BINARY_OVERRIDE = codegen_cmd or config.get('codegen', 'shell_command')
    global codegen_start, codegen_duration
    codegen_start = sample_start \
                    or int( config.get( 'codegen', 'sample_start') )
    codegen_duration = sample_duration \
                       or int( config.get( 'codegen', 'sample_duration') )
