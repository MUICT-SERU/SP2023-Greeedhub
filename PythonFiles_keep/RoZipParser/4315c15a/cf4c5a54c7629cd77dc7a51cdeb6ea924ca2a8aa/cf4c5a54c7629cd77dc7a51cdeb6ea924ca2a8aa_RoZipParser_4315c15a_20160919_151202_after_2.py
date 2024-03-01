from setuptools import setup, find_packages
from codecs import open
from os import path


here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="rozipparser",
    version="0.2.0",
    description="Parse official zip code documents from the Romanian Government",
    url="https://github.com/macostea/RoZipParser",
    author="Mihai Costea",
    author_email="mihai.andrei.costea@icloud.com",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
    ],
    keywords="zip code development parser romania",
    packages=find_packages(exclude=["tests"]),
    install_requires=["openpyxl"]
)
