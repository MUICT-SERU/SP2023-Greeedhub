#!/usr/bin/env python
# coding: utf-8

from __future__ import print_function

import os
import sys

from distutils.core import setup

pjoin = os.path.join
here = os.path.abspath(os.path.dirname(__file__))

# Get the current package version.
version_ns = {}
with open(pjoin(here, 'version.py')) as f:
   exec(f.read(), {}, version_ns)

# TODO: this
setup_args = dict(
    name = 'jupyterhub_raven_auth',
    url = 'https://github.com/PyCav/jupyterhub-raven-auth',
    packages = ['raven_auth', 'ibisclient'],
    include_package_data= True,
    version = version_ns['__version__']
)

if 'setuptools' in sys.modules:
    setup_args['install_requires'] = install_requires = []
    with open('requirements.txt') as f:
        for line in f.readlines():
            req = line.strip()
            if not req or req.startswith(('e', '#')):
                continue
            install_requires.append(req)

def main():
    setup(**setup_args)

if __name__ == '__main__':
    main()
