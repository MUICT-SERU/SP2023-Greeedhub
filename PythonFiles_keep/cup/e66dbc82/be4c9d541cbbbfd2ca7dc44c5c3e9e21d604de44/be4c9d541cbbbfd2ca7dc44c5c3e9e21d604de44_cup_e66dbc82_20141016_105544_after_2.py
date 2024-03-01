from distutils.core import setup

setup(
    name="cup",
    version="0.2.0",
    author="Pavan Mishra",
    author_email="pavanmishra@gmail.com",
    py_modules=["cup"],
    include_package_data=True,
    url="https://github.com/pavanmishra/cup",
    license="LICENSE",
    description="A pythonic interface to web.py",
	long_description=open("README.md").read(),
    install_requires=[
        "web.py",
    ],
)
