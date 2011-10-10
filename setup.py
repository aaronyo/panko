from setuptools import setup
import imp

tagconf = imp.load_source('tagmap_config', 'audiofile/tagmap_config.py')

foo.MyClass()

setup(
    entry_points = {
        'console_scripts': ['panko = panko.command.panko']
    }
    
)