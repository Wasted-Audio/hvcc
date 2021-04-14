import sys

from setuptools import setup

if sys.version_info < (3, 0):
    sys.exit('Sorry, Python <3 is not supported')


setup(name='hvcc',
      version='0.0.1',
      author='Enzien Audio, Wasted Audio',
      url='https://github.com/dromer/hvcc',
      packages=['hvcc'],
      install_requires=[
          'Jinja2==2.11.3'
      ],
      scripts=['bin/hvcc', 'bin/hvutil'])
