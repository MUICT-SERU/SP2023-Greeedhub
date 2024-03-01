# coding=utf-8
import os

from setuptools import setup
from setuptools.command.test import test as TestCommand
import sys
import re
import client

here = os.path.abspath(os.path.dirname(__file__))


class PyTest(TestCommand):
    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        import pytest
        errcode = pytest.main(self.test_args)
        sys.exit(errcode)


try:

    with open(here + '/README.md') as r:
        readme_html = r.read()
        readme_plain = re.sub(r"<([0-9a-zA-Z/]*)>", "", readme_html)

    with open(here + '/requirements.txt') as req:
        reqs = req.read().splitlines()
except:

    reqs = list()
    readme_plain = ''

setup(
    name='pyddsclient',
    version= client.__version__,
    download_url='https://github.com/eloylp/pyddsclient/tarball/' + client.__version__,
    url='https://github.com/eloylp/pyddsclient',
    license='GPLV3',
    author='Eloy (sbw)',
    install_requires=reqs,
    cmdclass={'test': PyTest},
    tests_require=['pytest'],
    author_email='eloy@sandboxwebs.com',
    description='',
    long_description=readme_plain,
    packages=['client'],
    classifiers=[
        'Programming Language :: Python :: 3 :: Only',
        'Development Status :: 4 - Beta',
        'Natural Language :: English',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: Freely Distributable',
        'Operating System :: POSIX :: Linux'
    ],
    include_package_data=True,
    platforms='any',
    scripts=['client/pyddsclient.py']
)
