"""Build pokrok.
"""
import os.path
import sys

from setuptools import setup, find_packages
import versioneer

setup(
    name = 'pokrok',
    version = versioneer.get_version(),
    cmdclass = versioneer.get_cmdclass(),
    author = 'John Didion',
    author_email = 'johndidion@gmail.com',
    url = 'https://github.com/jdidion/pokrok',
    description = 'Simple API for progress bars using any of several supported libraries',
    license = 'MIT',
    packages = find_packages(),
    tests_require = ['pytest'], #, 'jinja2', 'pysam'],
    extras_require = {
        'progressbar' : ['progressbar2'],
        'tqdm' : ['tqdm'],
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: User Interfaces",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3"
    ]
)
