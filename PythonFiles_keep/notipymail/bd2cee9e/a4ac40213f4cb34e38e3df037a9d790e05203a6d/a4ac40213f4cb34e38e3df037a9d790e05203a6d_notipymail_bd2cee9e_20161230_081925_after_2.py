#!/usr/bin/env python

from distutils.core import setup

setup(name='Notipy',
    version='1.0',
    description='Notipy Python Email Notifier',
    author='Nathan Bryans',
    author_email='io@nathanbryans.ca',
    packages=['notipylib'],
    package_data={'notipylib': ['data/*.dat', 'data/*.log']},
    )