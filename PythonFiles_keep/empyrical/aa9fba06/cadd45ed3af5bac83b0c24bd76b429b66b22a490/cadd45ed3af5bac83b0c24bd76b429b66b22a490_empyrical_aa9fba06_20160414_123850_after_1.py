#!/usr/bin/env python
from setuptools import setup

import versioneer


DISTNAME = 'pyrisk'
DESCRIPTION = "pyrisk is a Python library with performance and risk statistics commonly used in quantitative finance"
LONG_DESCRIPTION = """pyrisk is a Python library with performance and risk statistics
commonly used in quantitative finance by `Quantopian Inc`_. It is used by `Zipline`_ open source backtesting library as well as `pyfolio`_.

.. _Quantopian Inc: https://www.quantopian.com
.. _Zipline: http://zipline.io
.. _pyfolio: http://quantopian.github.io/pyfolio/
"""
MAINTAINER = 'Quantopian Inc'
MAINTAINER_EMAIL = 'opensource@quantopian.com'
AUTHOR = 'Quantopian Inc'
AUTHOR_EMAIL = 'opensource@quantopian.com'
URL = "https://github.com/quantopian/pyfolio"
LICENSE = "Apache License, Version 2.0"
VERSION = "0.1"

classifiers = ['Development Status :: 4 - Beta',
               'Programming Language :: Python',
               'Programming Language :: Python :: 2',
               'Programming Language :: Python :: 3',
               'Programming Language :: Python :: 2.7',
               'Programming Language :: Python :: 3.4',
               'License :: OSI Approved :: Apache Software License',
               'Intended Audience :: Science/Research',
               'Topic :: Scientific/Engineering',
               'Topic :: Scientific/Engineering :: Mathematics',
               'Operating System :: OS Independent']

install_reqs = [
    'numpy>=1.9.1',
    'pandas>=0.15.0',
    'scipy>=0.14.0',
]

test_reqs = ['nose>=1.3.7', 'nose-parameterized>=0.5.0']

if __name__ == "__main__":
    setup(
        name=DISTNAME,
        cmdclass=versioneer.get_cmdclass(),
        version=versioneer.get_version(),
        maintainer=MAINTAINER,
        maintainer_email=MAINTAINER_EMAIL,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        long_description=LONG_DESCRIPTION,
        packages=['pyrisk', 'pyrisk.tests'],
        classifiers=classifiers,
        install_requires=install_reqs,
        extras_requires=extras_reqs,
        tests_require=test_reqs,
        test_suite='nose.collector',
    )
