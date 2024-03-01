import os
from setuptools import setup
from icy import __version__

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

__doc__ = 'data wrangling glue code'

if __name__ == '__main__':
    setup(
        name = 'icy',
        version = __version__,
        description = __doc__,
        install_requires = ['pandas', 'pyyaml'],
        author = 'Jonathan Rahn',
        author_email = 'jr@rcs-analytics.com',
        url = 'https://github.com/rcs-analytics/icy',
        license = 'MIT',
        packages = ['icy'],
        long_description = read('README'),
    )
