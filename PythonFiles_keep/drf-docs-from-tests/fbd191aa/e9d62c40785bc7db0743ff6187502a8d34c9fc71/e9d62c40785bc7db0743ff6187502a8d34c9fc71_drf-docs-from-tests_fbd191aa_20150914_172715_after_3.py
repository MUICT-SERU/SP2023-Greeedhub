# -*- coding: utf-8 -*-

from django.conf import settings

# Template for wiki-page (default: gitlab.tpl)
BASE_TEMPLATE = getattr(settings, 'DOCSFROMTESTS_BASE_TEMPLATE', 'gitlab.tpl')

# Template for request-response (default: gitlab_request.tpl)
REQUEST_TEMPLATE = getattr(settings, 'DOCSFROMTESTS_REQUEST_TEMPLATE', 'gitlab_request.tpl')

# Path for saving generated docs (default: docs)
DOCS_PATH = getattr(settings, 'DOCSFROMTESTS_DOCS_PATH', 'docs')

# Dict of extra request kwargs (SERVER_NAME='example.com')
REQUEST_KWARGS = getattr(settings, 'DOCSFROMTESTS_REQUEST_KWARGS', {})

# Format of generated doc (default: md)
FILE_FORMAT = getattr(settings, 'DOCSFROMTESTS_FILE_FORMAT', 'md')
