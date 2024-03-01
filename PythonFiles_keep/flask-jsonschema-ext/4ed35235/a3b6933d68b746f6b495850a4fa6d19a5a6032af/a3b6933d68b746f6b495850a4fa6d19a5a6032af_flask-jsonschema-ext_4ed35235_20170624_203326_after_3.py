#!/usr/bin/env python
"""
Flask JSONSchema Extended Library

This library can be used to apply a JSONSchema (http://json-schema.org/) to a Flask API end-point that is generated on the fly from your database entities.

Currently supported drivers are:

* SQLAlchemy
"""

from setuptools import setup

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

with open('test-requirements.txt') as f:
    tests_requires = f.read().splitlines()

setup(name='Flask-JSONSchema-Ext',
      version='0.1.2',
      license='MIT',
      description='Flask JSONSchema Extended Library',
      long_description=__doc__,
      author='rachekalmir',
      author_email='rachekalmir@users.noreply.github.com',
      url='https://github.com/rachekalmir/flask-jsonschema-ext',
      packages=['flask_jsonschema_ext'],
      install_requires=install_requires,
      tests_requires=tests_requires,
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
