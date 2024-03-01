from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag(takes_context=True)
def breadcrumbs(context):
    """
    Provides the {% breadcrumbs %} tag to render a list of breadcrumbs.
    The rendered HTML will look something like this:

    <ul class="breadcrumbs-list">
        <li class="breadcrumb"><a href="..">...</a></li>
        ..
    </ul>
    """

    crumbs = context['request'].breadcrumbs
    if len(crumbs) == 0:
        return mark_safe('')

    s = '<ul class="breadcrumbs-list">'
    for bc in crumbs:
        s += '<li class="breadcrumb">'
        if bc.url:
            s += '<a href="{}">{}</a>'.format(bc.url, bc.name)
        else:
            s += bc.name
        s += '</li>'
    s += '</ul>'

    return mark_safe(s)
