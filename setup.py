from setuptools import setup, find_packages
import imp

setup(
    name='panko',
    packages=find_packages(),
    entry_points = { 'console_scripts':['panko = panko.command.pankocmd:main'] },
    package_data = { 'panko.audiofile': ['tagmap.yaml'] }
)