# -*- coding: utf-8 -*-
"""
   profiling
   ~~~~~~~~~

   An interactive profilier.

"""
from __future__ import with_statement

import os
import sys
from textwrap import dedent

from setuptools import find_packages, setup
from setuptools.command.install import install
from setuptools.command.test import test
from setuptools.extension import Extension

try:
    import __pypy__
except ImportError:
    __pypy__ = False


# include __about__.py.
__dir__ = os.path.dirname(__file__)
about = {}
with open(os.path.join(__dir__, 'profiling', '__about__.py')) as f:
    exec(f.read(), about)


# these files require specific python version or later.  they will be replaced
# with a placeholder which raises a runtime error on installation.
PYTHON_VERSION_REQUIREMENTS = {
    'profiling/remote/asyncio.py': (3, 4),
}
INCOMPATIBLE_PYTHON_VERSION_PLACEHOLDER = dedent('''
# -*- coding: utf-8 -*-
raise RuntimeError('Python {version} or later required.')
''').strip()


def requirements(filename):
    """Reads requirements from a file."""
    with open(filename) as f:
        return [x.strip() for x in f.readlines() if x.strip()]


# use pytest instead.
def run_tests(self):
    raise SystemExit(__import__('pytest').main(['-v']))
test.run_tests = run_tests


# replace files which are incompatible with the current python version.
def replace_incompatible_files():
    for filename, version_info in PYTHON_VERSION_REQUIREMENTS.items():
        if sys.version_info >= version_info:
            continue
        version = '.'.join(str(v) for v in version_info)
        code = INCOMPATIBLE_PYTHON_VERSION_PLACEHOLDER.format(version=version)
        with open(filename, 'w') as f:
            f.write(code)
run_install = install.run
install.run = lambda x: (replace_incompatible_files(), run_install(x))


# build profiling.speedup on cpython.
if __pypy__:
    ext_modules = []
else:
    ext_modules = [Extension('profiling.speedup', ['profiling/speedup.c'])]


setup(
    name='profiling',
    version=about['__version__'],
    license=about['__license__'],
    author=about['__author__'],
    maintainer=about['__maintainer__'],
    maintainer_email=about['__maintainer_email__'],
    platforms='linux',
    packages=find_packages(),
    ext_modules=ext_modules,
    entry_points={
        'console_scripts': ['profiling = profiling.__main__:cli']
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Software Development :: Debuggers',
    ],
    install_requires=requirements('requirements.txt'),
    tests_require=requirements('test/requirements.txt'),
    test_suite='...',
)
