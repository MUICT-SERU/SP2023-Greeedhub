#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='graphpy',
    version='0.3',
    author=['Claudia Lazara Poiet Sampedro',
            'Igor Neves Faustino',
            'Leticia Mazzo Portela'],
    url='https://github.com/igornfaustino/graphpy',
    description='package to manipulate graphs',
    license='MIT',
    packages=find_packages(),
    install_requires=[],
    # entry_points={
    #     'console_scripts': ['forecastio = displayforecastio.app:run'],
    # }
)
