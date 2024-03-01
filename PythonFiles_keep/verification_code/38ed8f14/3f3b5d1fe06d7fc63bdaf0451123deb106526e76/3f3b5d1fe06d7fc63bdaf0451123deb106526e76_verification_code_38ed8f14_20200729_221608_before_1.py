from setuptools import setup, find_packages

setup(
    name = 'verifycode',
    version = '0.2.1',
    keywords='verificationcode',
    description = 'a library for generate verificatio code png',
    license = 'MIT License',
    url = 'https://github.com/yeqown/verification_code',
    author = 'Yeqown',
    author_email = 'yeqown@gmail.com',
    packages = find_packages(),
    include_package_data = True,
    platforms = ['OSX', 'win'],
    install_requires = ['pillow'],
)
