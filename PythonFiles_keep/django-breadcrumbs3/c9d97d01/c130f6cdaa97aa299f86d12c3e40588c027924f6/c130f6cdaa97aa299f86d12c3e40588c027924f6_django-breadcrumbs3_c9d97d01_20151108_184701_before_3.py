from django.core.urlresolvers import reverse
from django.test import TestCase, override_settings

TEMPLATES_DJANGO_18 = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
            ],
        },
    },
]

@override_settings(
    ROOT_URLCONF='breadcrumbs3.tests.urls',
    INSTALLED_APPS=['breadcrumbs3'],
    # for Django <= 1.7
    TEMPLATE_CONTEXT_PROCESSORS=['django.core.context_processors.request'],
    # for Django >= 1.8
    TEMPLATES=TEMPLATES_DJANGO_18,
    MIDDLEWARE_CLASSES=['breadcrumbs3.middleware.BreadcrumbMiddleware'],
)
class BreadcrumbsTest(TestCase):

    @override_settings(BREADCRUMBS_HOME_LINK=False)
    def test_breadcrumbs_no_url(self):
        response = self.client.get(reverse('test_no_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            '<ul class="breadcrumbs-list"><li class="breadcrumb">Some title</li></ul>')

    @override_settings(BREADCRUMBS_HOME_LINK=False)
    def test_breadcrumbs_with_url(self):
        response = self.client.get(reverse('test_with_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            '<ul class="breadcrumbs-list"><li class="breadcrumb"><a href="/theres-just-no-stopping-in-a-white-zone/">Some other title</a></li></ul>')

    @override_settings(BREADCRUMBS_HOME_LINK=True)
    def test_breadcrumbs_no_url_with_home(self):
        response = self.client.get(reverse('test_no_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            '<ul class="breadcrumbs-list"><li class="breadcrumb"><a href="/">Home</a></li><li class="breadcrumb">Some title</li></ul>')

    @override_settings(BREADCRUMBS_HOME_LINK=True)
    def test_breadcrumbs_with_url_with_home(self):
        response = self.client.get(reverse('test_with_url'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response,
            '<ul class="breadcrumbs-list"><li class="breadcrumb"><a href="/">Home</a></li><li class="breadcrumb"><a href="/theres-just-no-stopping-in-a-white-zone/">Some other title</a></li></ul>')
