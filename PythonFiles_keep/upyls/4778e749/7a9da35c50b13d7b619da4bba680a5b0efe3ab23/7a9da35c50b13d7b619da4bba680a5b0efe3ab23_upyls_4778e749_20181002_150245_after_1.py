from setuptools import find_packages, setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='upyls',
    version='0.1.0',
    url='https://github.com/Corvan/upyls',
    license='LGPL v. 2.1',
    author='Lars Liedtke',
    author_email='LarsLiedtke@gmx.de',
    description='A collection of python utilities',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
            "Programming Language :: Python :: 3.7",
            "License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)",
            "Operating System :: OS Independent",
            "Topic :: Software Development :: Libraries :: Python Modules",
            "Topic :: Utilities"
        ]
)
