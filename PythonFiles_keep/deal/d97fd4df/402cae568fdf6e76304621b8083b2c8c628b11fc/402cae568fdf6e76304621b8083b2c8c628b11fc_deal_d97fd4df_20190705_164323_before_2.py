#!/usr/bin/env python3
# built-in
import os
import sys
from datetime import date
from pathlib import Path

# external
import sphinx_rtd_theme
from recommonmark.parser import CommonMarkParser
from recommonmark.transform import AutoStructify


sys.path.append(os.path.abspath('../'))
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.doctest',
    'sphinx.ext.todo',
    'sphinx.ext.coverage',
    'sphinx.ext.viewcode',
    'sphinx.ext.githubpages',
]

templates_path = ['_templates']
source_parsers = {
    '.md': CommonMarkParser,
}
source_suffix = ['.rst', '.md']
master_doc = 'index'

project = 'Deal'
copyright = '{}, Gram (@orsinium)'.format(date.today().year)
author = 'Gram (@orsinium)'

version = '2.2'
release = '2.2.1'

language = None
exclude_patterns = []
todo_include_todos = True

pygments_style = 'sphinx'
html_theme = 'sphinx_rtd_theme'
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]
html_logo = str(Path(__file__).parent.parent / 'logo.png')
html_theme_options = {
    'logo_only': True,
    'display_version': False,
    'style_external_links': True,
    'style_nav_header_background': '#2c3e50',
}


# -- Options for HTMLHelp output ------------------------------------------

# Output file base name for HTML help builder.
htmlhelp_basename = 'dealdoc'


# -- Options for LaTeX output ---------------------------------------------

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title,
#  author, documentclass [howto, manual, or own class]).
latex_documents = [
    (master_doc, 'deal.tex', 'Deal Documentation',
     '@orsinium', 'manual'),
]


# -- Options for manual page output ---------------------------------------

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [(master_doc, 'deal', 'Deal Documentation', [author], 1)]


# -- Options for Texinfo output -------------------------------------------

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
    (master_doc, 'deal', 'Deal Documentation',
     author, 'Deal', 'One line description of project.', 'Miscellaneous'),
]


# https://github.com/rtfd/recommonmark/blob/master/docs/conf.py
def setup(app):
    config = {
        # 'url_resolver': lambda url: github_doc_root + url,
        'auto_toc_tree_section': 'Contents',
        'enable_eval_rst': True,
    }
    app.add_config_value('recommonmark_config', config, True)
    app.add_transform(AutoStructify)
