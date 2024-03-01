from django.http import HttpResponse
from django.template import Template, RequestContext

breadcrumb_template_html = Template("""
{% load breadcrumbs %}
{% breadcrumbs %}
""")

def render(request):
    """
    Renders a simple template that calls the breadcrumbs templatetag.
    """
    context = RequestContext(request)
    return HttpResponse(breadcrumb_template_html.render(context=context))

def some_view_no_url(request):
    request.breadcrumbs('Some title', None)
    return render(request)

def some_view_with_url(request):
    from .tests import BreadcrumbsTest as test
    request.breadcrumbs('Some other title', test.s)
    return render(request)
