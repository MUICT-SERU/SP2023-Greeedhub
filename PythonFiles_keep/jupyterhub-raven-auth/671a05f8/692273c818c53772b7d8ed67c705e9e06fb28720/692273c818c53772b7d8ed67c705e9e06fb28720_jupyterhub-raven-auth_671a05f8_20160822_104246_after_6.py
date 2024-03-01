#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function
import os, sys

from setuptools import setup, find_packages, Extension

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

# Get the current package version.
version_ns = {}
with open(pjoin(here, 'version.py')) as f:
   exec(f.read(), {}, version_ns)

setup(
    name = 'jupyterhub_raven_auth',
    version = version_ns['__version__'],
    
    description='jupyterhub-raven-auth',
    long_description='University of Cambridge raven plugin for JupyterHub',

    author='pyCav Team 2016',
    author_email=' ',

    license='BSD',

    classifiers=[
        'Intended Audience :: Education',
        'Topic :: Education',

        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],

    keywords='jupyterhub raven cambridge',

    url = 'https://github.com/PyCav/jupyterhub-raven-auth',
    packages = ['raven_auth', 'ibisclient'],
    
    install_requires=['jupyterhub',
    'python-raven'],
)
