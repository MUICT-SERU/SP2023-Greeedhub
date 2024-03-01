#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# To generate DEB package from Python Package:
# sudo pip3 install stdeb
# python3 setup.py --verbose --command-packages=stdeb.command bdist_deb
#
#
# To generate RPM package from Python Package:
# sudo apt-get install rpm
# python3 setup.py bdist_rpm --verbose --fix-python --binary-only
#
#
# To generate EXE MS Windows from Python Package (from MS Windows only):
# python3 setup.py bdist_wininst --verbose
#
#
# To generate PKGBUILD ArchLinux from Python Package (from PyPI only):
# sudo pip3 install git+https://github.com/bluepeppers/pip2arch.git
# pip2arch.py PackageNameHere
#
#
# To Upload to PyPI by executing:
# python3 setup.py register
# python3 setup.py bdist_egg sdist --formats=bztar,gztar,zip upload --sign


"""Setup.py for Python, as Generic as possible."""

import os
import re
from setuptools import setup, find_packages


##############################################################################
# EDIT HERE


DESCRIPTION = ("StandAlone Async single-file cross-platform no-dependencies"
                 " Unicode-ready Python3-ready Minifier for the Web.")
REQUIREMENTS_FILE = os.path.join(os.path.dirname(__file__), "requirements.txt")


##############################################################################
# Dont touch below

def parse_metadata(path):
    """Parse file at 'path' and return metadata as a dictionary."""
    metadata = {}

    with open(path) as file:
        for line in file.readlines():
            if line.startswith('__'):
                line = line.strip()
                key, value  = line.split(sep='=')
                key = key.strip('_ ')
                if key == 'all':
                    continue
                print("Getting metadata for {what}.".format(what=key))
                if key not in metadata:
                    metadata[key] = value.strip("' ")

    return metadata


print("Starting build of setuptools.setup().")

# Generate metadata used by setuptools.setup()
metadata = parse_metadata('css_html_js_minify/__init__.py')

##############################################################################
# EDIT HERE

setup(

    name='css-html-js-minify',
    version=metadata.get('version'),

    description=DESCRIPTION,
    long_description=DESCRIPTION,

    url=metadata.get('url'),
    license=metadata.get('license'),

    author=metadata.get('author'),
    author_email=metadata.get('email'),
    maintainer=metadata.get('author'),
    maintainer_email=metadata.get('email'),

    packages=find_packages(),
    include_package_data=True,
    zip_safe=True,

    install_requires=['anglerfish'],
    setup_requires=['anglerfish'],
    tests_require=['anglerfish'],
    requires=['anglerfish'],

    scripts=['css-html-js-minify.py'],

    keywords=['CSS', 'HTML', 'JS', 'Compressor', 'CSS3', 'HTML5', 'Web',
              'Javascript', 'Minifier', 'Minify', 'Uglify', 'Obfuscator'],

    classifiers=[

        'Development Status :: 5 - Production/Stable',

        'Environment :: Console',

        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Other Audience',

        'Natural Language :: English',

        'License :: OSI Approved :: GNU General Public License (GPL)',
        'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',

        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: MacOS :: MacOS X',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',

        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',

        'Topic :: Software Development',

    ],
)


print('Finished build of setuptools.setup().')
