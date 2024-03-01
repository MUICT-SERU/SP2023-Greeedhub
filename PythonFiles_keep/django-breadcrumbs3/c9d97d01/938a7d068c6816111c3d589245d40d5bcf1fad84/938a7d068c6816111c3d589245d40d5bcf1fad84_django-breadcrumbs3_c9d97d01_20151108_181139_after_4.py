from django.conf import settings

class Breadcrumb(object):
    """
    A single breadcrumb, which is a 1:1 mapping to a view.
    This is simply a wrapper class for the template tag.
    """
    def __init__(self, name, url):
        self.name = name
        self.url = url

class Breadcrumbs(object):
    """
    The site's breadcrumbs. An instance of this class is added to each
    request, and can be called to add breadcrumbs to the template context.

    def some_view(request):
        request.breadcrumbs('Title', request.path_info)
        request.breadcrumbs('Subtitle', ...)
        ...

    You may prevent the 'Home' link being added by setting BREADCRUMBS_ADD_HOME
    to False (defaults to True).

    This class supports iteration, and is used as such in the template tag.
    """

    _bc = []

    def __init__(self, request):
        self._request = request

        # We must clear the list on every request or we will get duplicates
        del self._bc[:]

        # By default, add a link to the homepage. This can be disabled or
        # configured in the project settings.
        if getattr(settings, 'BREADCRUMBS_HOME_LINK', True):
            home_name = getattr(settings, 'BREADCRUMBS_HOME_LINK_NAME', 'Home')
            home_url = getattr(settings, 'BREADCRUMBS_HOME_LINK_URL', '/')
            self._add(home_name, home_url)

    def __call__(self, *args, **kwargs):
        return self._add(*args, **kwargs)

    def __iter__(self):
        return iter(self._bc)

    def __len__(self):
        return len(self._bc)

    def _add(self, name, url):
        self._bc.append(Breadcrumb(name, url))

class BreadcrumbMiddleware(object):
    """
    Middleware to add breadcrumbs into every request.

    Add 'breadcrumbs3.middleware.BreadcrumbMiddleware' to MIDDLEWARE_CLASSES
    and make sure 'django.template.context_processors.request' is in
    TEMPLATES.context_processors.
    """

    def process_request(self, request):
        request.breadcrumbs = Breadcrumbs(request)
