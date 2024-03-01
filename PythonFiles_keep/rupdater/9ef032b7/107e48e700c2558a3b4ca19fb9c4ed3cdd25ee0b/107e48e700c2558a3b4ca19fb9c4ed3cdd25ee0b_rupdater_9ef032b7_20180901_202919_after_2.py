#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os

from setuptools import setup

here = os.path.abspath(os.path.dirname(__file__))


def readme():
    with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
        return f.read()


setup(
    name='rupdater',
    version='1.1.1a1',
    description='Lightweight dependency free update software',
    long_description=readme(),
    long_description_content_type='text/markdown',
    license='GPLv3',
    author='Ranx',
    author_email='mod34@yandex.ru',
    url='https://github.com/r4nx/rupdater',
    py_modules=['rupdater'],
    keywords=['update', 'updater'],
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3.7',
        'Topic :: Software Development :: Libraries'
    ]
)
