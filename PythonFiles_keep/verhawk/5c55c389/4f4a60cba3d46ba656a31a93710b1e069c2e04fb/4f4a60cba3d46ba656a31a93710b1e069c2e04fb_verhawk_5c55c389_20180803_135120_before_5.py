from setuptools import setup, find_packages
import sys
sys.path.insert(1, 'relic')

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
