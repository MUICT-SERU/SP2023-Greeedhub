#!/usr/bin/env python
"""
Flask JSONSchema Extended Library

This library can be used to apply a JSONSchema (http://json-schema.org/) to a Flask API end-point that is generated on the fly from your database entities.

Currently supported drivers are:

* SQLAlchemy
"""

from setuptools import setup
from pip.req import parse_requirements

from flask_jsonschema_ext import __version__

install_requires = parse_requirements('requirements.txt')
test_requires = parse_requirements('test-requirements.txt')

setup(name='Flask-JSONSchema-Ext',
      version=__version__,
      license='MIT',
      description='Flask JSONSchema Extended Library',
      long_description=__doc__,
      author='rachekalmir',
      author_email='rachekalmir@users.noreply.github.com',
      url='https://github.com/rachekalmir/flask-jsonschema-ext',
      packages=['flask_jsonschema_ext'],
      install_requires=install_requires,
      tests_requires=test_requires,
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Python :: 3',
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      )
