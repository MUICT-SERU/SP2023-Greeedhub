# -*- coding: utf-8 -*-

from setuptools import setup


version = '1.1.2'


setup(
    name='pywe-oauth',
    version=version,
    keywords='Wechat Weixin Oauth Oauth2',
    description='Wechat Oauth Module for Python.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',

    url='https://github.com/sdkwe/pywe-oauth',

    author='Hackathon',
    author_email='kimi.huang@brightcells.com',

    packages=['pywe_oauth'],
    py_modules=[],
    install_requires=['pywe-base>=1.0.7', 'shortuuid', 'six'],

    classifiers=[
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
