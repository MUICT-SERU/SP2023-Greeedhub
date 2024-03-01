#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# To generate DEB package from Python Package:
# sudo pip3 install stdeb
# python3 setup.py --verbose --command-packages=stdeb.command bdist_deb
#
#
# To generate RPM package from Python Package:
# sudo apt-get install rpm
# python3 setup.py bdist_rpm --verbose --fix-python --binary-only
#
#
# To generate EXE MS Windows from Python Package (from MS Windows only):
# python3 setup.py bdist_wininst --verbose
#
#
# To generate PKGBUILD ArchLinux from Python Package (from PyPI only):
# sudo pip3 install git+https://github.com/bluepeppers/pip2arch.git
# pip2arch.py PackageNameHere
#
#
# To Upload to PyPI by executing:
# python3 setup.py register
# python3 setup.py bdist_egg sdist --formats=bztar,gztar,zip upload --sign


import os
import re

from setuptools import setup, Command
from tempfile import TemporaryDirectory
from shutil import copytree
from zipapp import create_archive


##############################################################################
# Dont touch below


class ZipApp(Command):
    description, user_options = "Creates a zipapp.", []

    def initialize_options(self): pass  # Dont needed, but required.

    def finalize_options(self): pass  # Dont needed, but required.

    def run(self):
        with TemporaryDirectory() as tmpdir:
            copytree('.', os.path.join(tmpdir, 'css-html-js-minify'))
            fyle = os.path.join(tmpdir, '__main__.py')
            with open(fyle, 'w', encoding='utf-8') as entry:
                entry.write("import runpy\nrunpy.run_module('css-html-js-minify')")
            create_archive(tmpdir, 'css-html-js-minify.pyz', '/usr/bin/env python3', "css-html-js-minify")


##############################################################################


setup(
    install_requires=['anglerfish'],
    setup_requires=['anglerfish'],
    tests_require=['anglerfish'],
    requires=['anglerfish'],

    # scripts=['css-html-js-minify.py'],  # uncomment if want install as script

    entry_points={
         'console_scripts': [
             "css-html-js-minify = css_html_js_minify.minify:main",
         ],
     },

    cmdclass={"zipapp": ZipApp},
)
