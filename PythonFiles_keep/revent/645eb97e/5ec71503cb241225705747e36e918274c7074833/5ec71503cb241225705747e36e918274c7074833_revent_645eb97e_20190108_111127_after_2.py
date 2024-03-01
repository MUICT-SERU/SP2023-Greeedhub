#!/usr/bin/env python

from setuptools import setup

name = "revent"
author = "lwzm"

with open("README.md") as f:
    long_description = f.read()


setup(
    name=name,
    version="1.7",
    description="Event util base on Redis",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=author,
    author_email="{}@qq.com".format(author),
    keywords="redis event util".split(),
    url="https://github.com/{}/{}".format(author, name),
    packages=["revent"],
    install_requires="redis".split(),
    classifiers=[
        "Environment :: Console",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
    ],
)
