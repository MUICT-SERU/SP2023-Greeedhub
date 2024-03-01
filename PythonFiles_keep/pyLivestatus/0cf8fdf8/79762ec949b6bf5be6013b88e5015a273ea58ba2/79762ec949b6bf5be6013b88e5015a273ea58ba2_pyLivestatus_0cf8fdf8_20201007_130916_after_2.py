"""
pyLivestatus Library
-------------------
Livestatus Library for support reading from Livestatus socket
"""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='pyLivestatus',
                 version='1.0.4',
                 url='https://github.com/ElmecOSS/pyLivestatus',
                 license='MIT',
                 author='Luca Depaoli',
                 author_email='luca.depaoli@elmec.it',
                 description='Python library for Livestatus Integration',
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 keywords=['pyLivestatus', 'nagios', 'nagios socket'],
                 packages=setuptools.find_packages(),
                 zip_safe=False,
                 platforms='any',
                 install_requires=[],
                 classifiers=[
                     'Development Status :: 1 - Planning',
                     'Environment :: Web Environment',
                     'Intended Audience :: Developers',
                     'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
                     'Operating System :: OS Independent',
                     'Programming Language :: Python',
                     'Topic :: Software Development :: Libraries :: Python Modules'
                 ])
