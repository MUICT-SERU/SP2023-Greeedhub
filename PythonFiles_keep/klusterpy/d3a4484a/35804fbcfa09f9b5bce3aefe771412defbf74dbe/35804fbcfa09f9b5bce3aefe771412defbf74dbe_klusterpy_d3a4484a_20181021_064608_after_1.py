import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="klusterpy",
    version="0.0.1",
    author="Erick Wijaya",
    author_email="wijaya.erick52@gmail.com",
    description="Python Data Mining Clustering Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wijayaerick/klusterpy",
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    python_requires='>=3',
    classifiers=[
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Education",
        "Topic :: Scientific/Engineering :: Artificial Intelligence"
    ],
)