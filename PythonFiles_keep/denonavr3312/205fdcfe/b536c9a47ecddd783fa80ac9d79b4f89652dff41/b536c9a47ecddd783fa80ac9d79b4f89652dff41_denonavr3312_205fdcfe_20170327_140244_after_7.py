#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(
    name='denonavr3312',
    version='0.0.0',
    packages=find_packages(),
    url='',
    license='',
    author='Florent Captier',
    author_email='florent@captier.org',
    description='Control Denon AVR 3312 through telnet interface',
    #zip_safe=False,
    tests_require=['tox']
)
