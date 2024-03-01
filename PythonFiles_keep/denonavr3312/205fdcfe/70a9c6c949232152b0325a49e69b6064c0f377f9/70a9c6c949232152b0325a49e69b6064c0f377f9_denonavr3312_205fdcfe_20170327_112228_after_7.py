#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='denonavr3312',
    version='0.0.0',
    packages=['denonavr3312'],
    url='',
    license='',
    author='Florent Captier',
    author_email='florent@captier.org',
    description='Control Denon AVR 3312 through telnet interface',
    requires=open('requirements.txt', 'r').readlines()
)
