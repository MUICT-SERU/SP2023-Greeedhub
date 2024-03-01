#!/usr/bin/env python

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(name='varys',
      version='0.5',
      author='Ben Acland',
      author_email='benacland@gmail.com',
      description='For parsing and reformatting behavioral data.',
      license='BSD',
      keywords='behavioral',
      url='https://github.com/beOn/varys',
      install_requires=['scipy','chardet'],
      packages=['varys'],
      long_description=read('README.md'),
      classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Topic :: Scientific/Engineering :: Information Analysis',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
      ],
)