#!/usr/bin/env python
"""

"""

from distutils.core import setup

from flask_jsonschema_ext import __version__

setup(name='Flask-JSONSchema-Ext',
      version=__version__,
      license='MIT',
      description='Flask JSONSchema Extended Library',
      long_description=__doc__,
      author='rachekalmir',
      author_email='rachekalmir@users.noreply.github.com',
      url='https://github.com/rachekalmir/flask_jsonschema_ext',
      packages=['flask_jsonschema_ext'],
      install_requires=['sqlalchemy>=1.0.0', 'flask>=0.11.0', 'jsonschema>=2.6.0'],
      tests_requires=['pytest>=3.0'],
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
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
          'Topic :: Software Development :: Libraries :: Python Modules'
      ],
      )
