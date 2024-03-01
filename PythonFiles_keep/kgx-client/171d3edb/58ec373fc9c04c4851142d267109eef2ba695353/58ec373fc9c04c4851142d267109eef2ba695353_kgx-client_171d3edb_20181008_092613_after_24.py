from warnings import warn
try:
    import oscar
    from django.conf import settings
except ImportError:
    raise ImportError('django-oscar is required to use this package')


if 'KGX' not in settings:
    raise warn('Configuration for KG Express missing from django settings.')
