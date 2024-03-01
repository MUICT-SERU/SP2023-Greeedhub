"""izi/defaults.py

Defines and stores IZIR's default handlers

Copyright (C) 2018 IZI Global

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
documentation files (the "Software"), to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and
to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or
substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED
TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF
CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
OTHER DEALINGS IN THE SOFTWARE.

"""
from __future__ import absolute_import

import izi

output_format = izi.output_format.json

input_format = {
    'application/json': izi.input_format.json,
    'application/x-www-form-urlencoded': izi.input_format.urlencoded,
    'multipart/form-data': izi.input_format.multipart,
    'text/plain': izi.input_format.text,
    'text/css': izi.input_format.text,
    'text/html': izi.input_format.text
}

directives = {
    'timer': izi.directives.Timer,
    'api': izi.directives.api,
    'module': izi.directives.module,
    'current_api': izi.directives.CurrentAPI,
    'api_version': izi.directives.api_version,
    'user': izi.directives.user,
    'session': izi.directives.session,
    'documentation': izi.directives.documentation
}


def context_factory(*args, **kwargs):
    return dict()


def delete_context(context, exception=None, errors=None, lacks_requirement=None):
    del context
