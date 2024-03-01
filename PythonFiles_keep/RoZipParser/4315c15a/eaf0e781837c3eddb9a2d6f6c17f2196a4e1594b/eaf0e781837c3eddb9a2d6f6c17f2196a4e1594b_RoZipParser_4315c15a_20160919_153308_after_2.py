from setuptools import setup, find_packages
from codecs import open
from os import path

try:
    import pypandoc
    long_description = pypandoc.convert("README.md", "rst")
except(IOError, ImportError):
    long_description = "Parse official zip code documents from the Romanian Government"

setup(
    name="rozipparser",
    version="0.2.1",
    description="Parse official zip code documents from the Romanian Government",
    long_description=long_description,
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
