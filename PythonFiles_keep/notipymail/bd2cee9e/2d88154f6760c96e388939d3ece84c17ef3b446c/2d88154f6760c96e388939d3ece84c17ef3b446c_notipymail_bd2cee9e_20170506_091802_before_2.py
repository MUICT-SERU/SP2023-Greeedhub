#!/usr/bin/env python

"""
See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""

from distutils.core import setup

setup(
    name='notipymail',
    packages=['notipymail'],
    version='0.6',
    description='A full featured email status notifier for python',
    author='Nathan Bryans',
    author_email='io@nathanbryans.ca',
    url = 'https://github.com/nbryans/notipymail',
    download_url = 'https://github.com/nbryans/notipymail/tarball/0.1',
    license='MIT',
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 4 - Beta',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Communications :: Email',
        'Topic :: System :: Monitoring',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
    ],
    keywords = ['Email', 'Notifier', 'Status'],
    package_data={'notipymail': ['data/*.dat', 'data/*.log']},
)