import os
from setuptools import setup, find_packages


def read(*paths):
    """Build a file path from *paths* and return the contents."""
    with open(os.path.join(*paths), 'r') as f:
        return f.read().strip()

version = read('datastoredict/VERSION')

setup(
    name='datastoredict',
    version=version,
    description='A durabledict implementation for AppEngine.',
    url='https://github.com/vendasta/datastoredict',
    license='Apache 2.0',
    author='Kevin Sookocheff',
    author_email='ksookocheff@vendasta.com',
    packages=find_packages(exclude=['tests*']),
    package_data={
        'datastoredict': ['VERSION'],
    },
    install_requires=['durabledict'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
