#coding=utf-8
from setuptools import setup

setup(
    name = "PyNfeTrust",
    version = "0.1",
    author = "Danimar Ribeiro",
    author_email = 'danimaribeiro@gmail.com',
    test_suite='tests',
    keywords = ['nfe', 'mdf-e'],
    classifiers=[
        'Development Status :: 1 - alpha',
        'Environment :: Plugins',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v2 or later (LGPLv2+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages = [
        'pynfe',
        'pynfe.servicos',
    ],
    url = 'https://github.com/danimaribeiro/PyNfeTrust',
    license = 'LGPL-v2.1+',
    description = 'PyNfeTrust é uma biblioteca para envio de NF-e',
    long_description = 'PyNfeTrust',
    install_requires=[
        'PyXMLSec >= 0.3.0'
    ],
    tests_require=[
        'pyflakes>=0.6.1',
    ],
)
