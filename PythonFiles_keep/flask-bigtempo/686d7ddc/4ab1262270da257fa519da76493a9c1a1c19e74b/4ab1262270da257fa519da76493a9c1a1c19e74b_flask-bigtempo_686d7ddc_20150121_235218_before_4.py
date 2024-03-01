#!/usr/bin/env python
# -*- coding: utf-8 -*-


'''
Flask-BigTempo
--------------

Flask extension created to enable a flask server to provide bigtempo functions.
'''


import os
import re

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


import flask_bigtempo


def read(*rnames):
    return open(os.path.join(os.path.dirname(__file__), *rnames)).read()


def filter_comments(contents):
    filter_pattern = re.compile(r'[\s]*#.*')
    return filter(lambda x: not filter_pattern.match(x), contents)


setup(
    name='flask-bigtempo',
    version=flask_bigtempo.__version__,
    description="Flask extension for bigtempo features",
    long_description=read('README.md'),
    license=read('LICENSE'),

    author="Roberto Haddock Lobo",
    author_email="rhlobo+bigtempo@gmail.com",
    url='https://github.com/rhlobo/flask-bigtempo',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Financial and Insurance Industry',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
        'Topic :: Scientific/Engineering',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    platforms='any',

    install_requires=filter_comments(read('requirements.txt').split('\n')),
    packages=['flask_bigtempo'],
    package_data={'': ['README.md',
                       'LICENSE',
                       'requirements.txt']},

    include_package_data=True,
    zip_safe=False
)
