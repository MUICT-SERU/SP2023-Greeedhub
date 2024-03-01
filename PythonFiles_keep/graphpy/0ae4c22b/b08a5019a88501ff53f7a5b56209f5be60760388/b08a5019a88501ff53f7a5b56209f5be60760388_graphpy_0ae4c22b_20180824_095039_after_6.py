#!/usr/bin/env python

from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='graphpython',
    version='0.83',
    author='Claudia Lazara Poiet Sampedro, Igor Neves Faustino, Leticia Mazzo Portela',
    author_email='clp.sampedro@gmail.com, igornfaustino@gmail.com, leticiaportela@alunos.utfpr.edu.br',
    url='https://github.com/igornfaustino/graphpy',
    description='package to manipulate graphs',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=find_packages(),
    install_requires=["six"],
    # entry_points={
    #     'console_scripts': ['forecastio = displayforecastio.app:run'],
    # }
)
