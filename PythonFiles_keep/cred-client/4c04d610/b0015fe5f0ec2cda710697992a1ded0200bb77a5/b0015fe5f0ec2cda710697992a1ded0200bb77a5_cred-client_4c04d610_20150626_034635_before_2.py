""" Setup file for the cred-client package. """
from setuptools import setup
import sys

# The package only works with python >=3.0
if sys.version_info < (3,):
    print("I'm only for 3, please upgrade")
    sys.exit(1)

version = '0.2.5'

setup(
    name='cred-client',
    version=version,
    author='Tehnix',
    author_email='ckl@codetalk.io',
    packages=['cred'],
    include_package_data=True,
    scripts=[],
    url='https://github.com/Tehnix/cred-client',
    download_url='https://github.com/Tehnix/cred-client/tarball/v{0}'.format(version),
    license='BSD',
    description='Client Library for cred-server.',
    # long_description=open('README.md').read(),
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3 :: Only',
        'Topic :: Home Automation',
    ],
    install_requires=[],
    #test_suite='nose.collector',
)
