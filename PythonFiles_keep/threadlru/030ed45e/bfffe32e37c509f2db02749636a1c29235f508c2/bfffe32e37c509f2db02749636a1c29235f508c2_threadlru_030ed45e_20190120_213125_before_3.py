from setuptools import setup, find_packages

setup(
    name="pqdict",
    version="0.0.1",
    url='https://github.com/mattpaletta/pqdict',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],
    setup_requires=[],
    author="Matthew Paletta",
    author_email="mattpaletta@gmail.com",
    description="Thread-Safe PQDict Implementation",
    license="BSD",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Communications',
    ]
)