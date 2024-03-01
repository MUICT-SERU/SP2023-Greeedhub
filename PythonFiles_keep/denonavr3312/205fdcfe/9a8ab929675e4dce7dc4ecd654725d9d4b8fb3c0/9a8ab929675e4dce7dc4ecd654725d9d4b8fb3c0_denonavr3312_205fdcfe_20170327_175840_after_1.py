#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='denonavr3312',
    version='0.1.0',
    packages=find_packages(),
    url='https://github.com/gyzpunk/denonavr3312',
    license='GNU',
    author='Florent Captier',
    author_email='florent@captier.org',
    description='Control Denon AVR 3312 through telnet interface',
    tests_require=['tox', 'pytest'],
    platforms=['any'],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Home Automation",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
    ]
)
