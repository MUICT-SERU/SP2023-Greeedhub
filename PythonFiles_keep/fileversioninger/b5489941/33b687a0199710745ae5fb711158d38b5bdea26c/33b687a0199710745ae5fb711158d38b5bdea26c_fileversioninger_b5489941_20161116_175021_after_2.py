from setuptools import setup

setup(
    name='fileversioninger',
    version='0.5',
    download_link='https://github.com/dwickstrom/fileversioninger/tarball/0.5 ',
    author='David Wickstrom',
    author_email='davidwickstrom@gmail.com',
    packages=['fileversioninger', 'tests'],
    url='https://github.com/dwickstrom/fileversioninger',
    license='MIT',
    description='Easily append a meaningful file name to the end of a given file name.',
	classifiers=[ "Intended Audience :: Developers"
				, "License :: OSI Approved :: BSD License"
				, "Operating System :: OS Independent"
				, "Programming Language :: Python :: 2.7"
				, "Programming Language :: Python :: 3"
				, "Topic :: Software Development"
				, "Topic :: Software Development :: Libraries"
				, "Topic :: Utilities"
				],
)
