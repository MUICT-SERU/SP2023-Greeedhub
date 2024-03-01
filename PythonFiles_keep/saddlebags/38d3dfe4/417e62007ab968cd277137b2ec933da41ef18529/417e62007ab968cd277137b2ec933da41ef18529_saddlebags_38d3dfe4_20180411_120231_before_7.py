from setuptools import setup, find_packages

setup(
    name="saddlebags",
    license="MIT",
    packages=find_packages(),
    version='1.2',
    author="Michael Dunn",
    author_email="mike@eikonomega.com",
    keywords='configuration settings',
    url="https://github.com/eikonomega/saddlebags",
    description=(
        "Saddlebags provides easy loading and access to "
        "the data elements of JSON/YAML configuration files."),
    install_requires=[
        'pytest>=3,<4',
        'PyYAML>=3.12,<4'
    ],
    package_data={
        '': ['requirements.txt']
    },
    classifiers=[
        'Intended Audience :: Developers',
        'Development Status :: 3 - Alpha',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ]
)

