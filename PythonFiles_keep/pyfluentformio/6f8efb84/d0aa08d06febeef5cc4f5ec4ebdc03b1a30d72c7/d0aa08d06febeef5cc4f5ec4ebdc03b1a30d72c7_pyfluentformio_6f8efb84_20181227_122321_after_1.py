from setuptools import setup

# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='pyfluentformio',
    url='https://github.com/Goat-Lab/pyfluentformio',
    author='Tomas Castro',
    author_email='tomas.castro@goatlab.io',
    # Needed to actually package something
    packages=['pyfluent'],
    download_url='https://github.com/Goat-Lab/pyfluentformio/archive/v0.1.2.tar.gz',
    keywords=['fluent', 'form.io', 'formio'],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        # Specify which pyhton versions that you want to support
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    # Needed for dependencies
    install_requires=['requests', 'pandas'],
    # *strongly* suggested for sharing
    version='0.1.2',
    # The license can be anything you like
    license='MIT',
    description='Fluent wrapper for creating requests to Form.io',
    # We will also need a readme eventually (there will be a warning)
    long_description=long_description,
    long_description_content_type='text/markdown'
)
