from distutils.core import setup
setup(
  name = 'UTF8 Code Point Checker',
  packages = ['utf8_codepoint'], # this must be the same as the name above
  version = '1.0.0',
  license='MIT',
  description = 'python library to make and get the encoding of unicode code point in UTF8.',
  author = 'Yanwar Solahudin',
  author_email = 'yanwarsolahudinn@gmail.com',
  url = 'https://github.com/yanwarsolahudinn/utf8-codepoint', # use the URL to the github repo
  download_url = 'https://github.com/yanwarsolahudinn/utf8-codepoint/tarball/1.0.0', # I'll explain this in a second
  keywords = ['utf8', 'library', 'code point', 'checking', 'hex', 'bin'], # arbitrary keywords
  classifiers = [
    'Development Status :: 3 - Alpha',

    # Indicate who your project is intended for
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',

    # Pick your license as you wish (should match "license" above)
    'License :: OSI Approved :: MIT License',

    # Specify the Python versions you support here. In particular, ensure
    # that you indicate whether you support Python 2, Python 3 or both.
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
  ],
)
