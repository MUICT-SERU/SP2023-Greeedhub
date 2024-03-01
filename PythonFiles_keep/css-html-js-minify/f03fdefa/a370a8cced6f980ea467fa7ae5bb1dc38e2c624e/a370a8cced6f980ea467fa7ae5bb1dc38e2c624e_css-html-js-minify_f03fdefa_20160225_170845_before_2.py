
__version__ = '1.9.0'
__license__ = 'GPLv3+ LGPLv3+'
__author__ = 'Juan Carlos'
__email__ = 'juancarlospaco@gmail.com'
__url__ = 'https://github.com/juancarlospaco/css-html-js-minify'
__source__ = ('https://raw.githubusercontent.com/juancarlospaco/'
              'css-html-js-minify/master/css-html-js-minify.py')

from .minify import process_single_html_file, process_single_js_file, process_single_css_file, \
    html_minify, js_minify, css_minify

__all__ = ['process_single_html_file', 'process_single_js_file', 'process_single_css_file',
    'html_minify', 'js_minify', 'css_minify', 'minify']


