#!/usr/bin/env python

"""
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from distutils.core import setup

# Thanks to StackOverflow user jakub-jirutka http://stackoverflow.com/users/2217862 for this snippet:
# http://stackoverflow.com/questions/10718767
try:
    from pypandoc import convert
    read_md = lambda f: convert(f, 'rst')
except ImportError:
    print("warning: pypandoc module not found, could not convert Mardown to RST")
    read_md = lambda f: open(f, 'r').read()

setup(
    name='notipymail',
    packages=['notipymail'],
    version='1.0',
    description='A full featured email status notifier for python',
    long_description = read_md('README.md'),
    author='Nathan Bryans',
    author_email='io@nathanbryans.ca',
    url = 'https://github.com/nbryans/notipymail',
    download_url = 'https://github.com/nbryans/notipymail/tarball/0.1',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Topic :: System :: Monitoring',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = ['Email', 'Notifier', 'Status'],
    package_data={'': ['README.md', 'LICENSE.txt'],    'notipymail': ['data/*.dat', 'data/*.log']},
)