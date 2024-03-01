"""
Flask-Perf
-------------


"""
from setuptools import setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name="Flask-Perf",
    version="0.1.4",
    url="https://github.com/abetlen/Flask-Perf",
    license="MIT",
    author="Andrei Betlen",
    author_email="abetlen@gmail.com",
    description="A simple profiler for flask applications.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=["flask_perf"],
    test_suite="test_flask_perf",
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "Flask"
    ],
    extras_require = {
        "flask_sqlalchemy": {
            "flask_sqlalchemy"
        }
    },
    tests_require=[
        "mock",
        "coverage",
        "flask_sqlalchemy"
    ],
    classifiers=[
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules"
    ]
)
