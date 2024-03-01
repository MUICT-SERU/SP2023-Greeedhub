#!/usr/bin/env python

from distutils.core import setup

setup(
    name='notipymail',
    packages=['notipymail'],
    version='0.1',
    description='A full featured Email notifier for python',
    author='Nathan Bryans',
    author_email='io@nathanbryans.ca',
    url = 'https://github.com/nbryans/notipymail',
    download_url = 'https://github.com/nbryans/notipymail/tarball/0.1',
    keywords = ['email', 'notifier', 'status'],
    package_data={'notipymail': ['data/*.dat', 'data/*.log']},
    classifiers = [],
    )