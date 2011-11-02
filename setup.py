from setuptools import setup, find_packages
import imp

setup(
    name='panko',
    packages=find_packages(),
    install_requires = ['mutagen', 'PIL', 'pyyaml', 'lxml', 'requests', 'pyechonest'],
    entry_points = { 'console_scripts':['panko = panko.main:main'] },
    package_data = { 'panko.audiofile': ['tagmap.yaml'], 'panko.command': ['lastfm.ini', 'echonest.ini'] }
)
