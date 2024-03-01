"""
Flask-Perf
-------------


"""
from setuptools import setup


setup(
    name="Flask-Perf",
    version="1.0",
    url="",
    license="MIT",
    author="Andrei Betlen",
    author_email="abetlen@gmail.com",
    description="A simple profiler for flask applications.",
    long_description=__doc__,
    py_modules=["flask_perf"],
    test_suite="test_flask_perf",
    zip_safe=False,
    include_package_data=True,
    platforms="any",
    install_requires=[
        "Flask"
    ],
    extra_require = {
        "flask_sqlalchemy": {
            "Flask-SQLALchemy"
        }
    },
    test_require=[],
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
