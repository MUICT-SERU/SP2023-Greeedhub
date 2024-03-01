import os
import pkgutil
import sys
from setuptools import setup, find_packages
from subprocess import check_call, CalledProcessError


if not pkgutil.find_loader('relic'):
    relic_local = os.path.exists('relic')
    relic_submodule = (relic_local and
                       os.path.exists('.gitmodules') and
                       not os.listdir('relic'))
    try:
        if relic_submodule:
            check_call(['git', 'submodule', 'update', '--init', '--recursive'])
        elif not relic_local:
            check_call(['git', 'clone', 'https://github.com/spacetelescope/relic.git'])

        sys.path.insert(1, 'relic')
    except CalledProcessError as e:
        print(e)
        exit(1)

import relic.release

NAME = 'verhawk'
version = relic.release.get_info()
relic.release.write_template(version, NAME)

setup(
    name=NAME,
    version=version.pep386,
    author='Joseph Hunkeler',
    author_email='jhunk@stsci.edu',
    description='Extract version data from Python [sub]packages/modules',
    url='https://github.com/spacetelescope/verhawk',
    license='BSD',
    classifiers=[
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    packages=find_packages(),
    package_data={'': ['README.md', 'LICENSE.txt']},
    entry_points={
        'console_scripts': [
            'verhawk = verhawk.cli.verhawk:main'
        ]
    },
)
