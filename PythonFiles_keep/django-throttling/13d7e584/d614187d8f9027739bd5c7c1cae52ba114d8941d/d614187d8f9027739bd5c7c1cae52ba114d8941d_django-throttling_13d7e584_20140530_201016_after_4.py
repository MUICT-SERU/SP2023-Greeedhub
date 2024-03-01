#!/usr/bin/env python
# encoding: utf-8
from setuptools import setup, find_packages
from pip.req import parse_requirements

install_reqs = parse_requirements("requirements.txt")
reqs = [str(each.req) for each in install_reqs if each.req]
install_reqs = parse_requirements("requirements.txt")
links = [str(each.url) for each in install_reqs if each.url]

setup(
    name             = 'Django-Throttling',
    version          = '1.1.2',
    author           = "Diogo Laginha",
    url              = 'https://github.com/laginha/django-throttling',
    description      = "Throttling for Django",
    packages         = find_packages(where='src'),
    package_dir      = {'': 'src'},
    install_requires = reqs,
    dependency_links = links,
    extras_require   = {},
    zip_safe         = False,
)
