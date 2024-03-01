from os.path import dirname, join, abspath
from setuptools import setup, find_packages

ROOT_DIR = dirname(abspath(__file__))

setup(
    packages=find_packages(where=join(ROOT_DIR, 'src')),
    package_dir={'kgx': 'src/kgx'},
    include_package_data=True,
    platforms='any'
)
