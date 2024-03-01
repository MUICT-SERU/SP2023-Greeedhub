'''
Use of this source code is governed by a MIT-style license that can be found in the LICENSE file.
Created on Jan 27, 2017
@author: Niels Lubbes

https://python-packaging.readthedocs.io/en/latest/minimal.html
https://pypi.python.org/pypi?%3Aaction=list_classifiers
'''


from setuptools import setup


def readme():
    with open( 'README.md' ) as f:
        return f.read()


setup( name = 'ns_lattice',
       version = '1.0',
       description = 'Algorithms for Neron-Severi lattice',
       long_description = readme(),
       classifiers = [
           'Development Status :: 3 - Alpha',
           'License :: OSI Approved :: MIT License',
           'Programming Language :: Python :: 2.7',
           'Topic :: Scientific/Engineering :: Mathematics',
           ],
      keywords = 'Neron-Severi-lattice',
      url = 'http://github.com/niels-lubbes/ns_lattice',
      author = 'Niels Lubbes',
      license = 'MIT',
      package_dir = {'': 'src'},
      packages = ['linkage'],
      # install_requires = ['markdown'],
      # dependency_links = ['http://github.com/niels-lubbes/linear_series/tarball/master#egg=package-1.0'],
      test_suite = 'nose.collector',
      tests_require = ['nose'],
      entry_points = {
          'console_scripts': ['run-lattice=ns_lattice.__main__:main'],
      },
      include_package_data = True,
      zip_safe = False )


