from setuptools import setup, find_packages

def readme():
    with open('README.md') as f:
        return f.read()

setup(
    name='fuzzyfloat',
    version='1.0.1.dev1',
    description='Utility library that provides a floating point type with tolerance for equality comparisons',
    long_description=readme(),
    long_description_content_type="text/markdown",
    url='https://github.com/keystonetowersystems/fuzzyfloat',
    author='Greg Echelberger',
    author_email='greg@keystonetowersystems.com',
    packages=find_packages(exclude=('tests',)),
    install_requires=[],
    python_requires='>=3',
    setup_requires=[
        "nose>=1.3.7"
    ],
    test_suite="nose.collector",
    zip_safe=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: MIT License",
        "Topic :: Scientific/Engineering",
        "Operating System :: OS Independent",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
    ],
)
