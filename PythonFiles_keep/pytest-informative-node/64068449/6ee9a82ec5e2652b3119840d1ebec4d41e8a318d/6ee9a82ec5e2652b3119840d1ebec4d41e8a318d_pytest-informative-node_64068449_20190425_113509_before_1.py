#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-informative-node',
    version='0.1.2',
    author='megachweng',
    author_email='megachweng@gmail.com',
    maintainer='megachweng',
    maintainer_email='megachweng@gmail.com',
    license='MIT',
    url='https://github.com/megachweng/pytest-informative-node',
    description='display more node ininformation.',
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    py_modules=['pytest_informative_node'],
    python_requires='>=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*',
    install_requires=['pytest>=3.10.0'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'informative-node = pytest_informative_node',
        ],
    },
)
