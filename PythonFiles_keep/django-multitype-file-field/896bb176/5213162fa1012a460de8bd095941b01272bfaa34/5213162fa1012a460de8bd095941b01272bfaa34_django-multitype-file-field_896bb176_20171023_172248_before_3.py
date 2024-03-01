# coding: utf-8
# !/usr/bin/env python
import os
from setuptools import setup, find_packages

__doc__ = """App for Django featuring improved form base classes."""

project_name = 'django-multitype-file-field'

version = '0.0.4'

ROOT = os.path.dirname(__file__)


def read(fname):
    return open(os.path.join(ROOT, fname)).read()

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except ImportError:
    long_description = read('README.md')


setup(
    name=project_name,
    version=version,
    description=__doc__,
    long_description=long_description,
    url="https://github.com/Apkawa/django-multitype-file-field",
    author="Apkawa",
    author_email='apkawa@gmail.com',
    packages=[package for package in find_packages() if package.startswith(project_name)],
    install_requires=['six'],
    zip_safe=False,
    include_package_data=True,
    keywords=['django'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Framework :: Django',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.9',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Topic :: Internet :: WWW/HTTP',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
)
