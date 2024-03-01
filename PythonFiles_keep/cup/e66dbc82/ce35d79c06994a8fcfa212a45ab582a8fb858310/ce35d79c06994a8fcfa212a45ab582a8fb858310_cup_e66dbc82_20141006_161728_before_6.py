from distutils.core import setup

setup(
    name="dispel",
    version="0.1.0",
    author="Pavan Mishra",
    author_email="pavanmishra@gmail.com",
    py_modules=["dispel"],
    include_package_data=True,
    url="https://github.com/pavanmishra/dispel",
    license="LICENSE",
    description="it's web.py, stupid, but dispelled",
	long_description=open("README.md").read(),
    install_requires=[
        "web.py",
    ],
)
