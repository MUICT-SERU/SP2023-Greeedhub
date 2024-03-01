from pprint import pprint
from unittest.case import TestCase

# from django.test import TestCase
from django_pythonic_menu.menu import Menu, MenuItem
from django_pythonic_menu import menu
from django_pythonic_menu.templatetags.pythonic_menu import render_menu


class UserLike:
    is_authenticated = True


class RequestLike:
    user = UserLike()


def dummy_reverse(route_name):
    return 'route:' + route_name


# Create your tests here.
class MenuTest(TestCase):
    def setUp(self):
        self.reverse = menu.reverse
        menu.reverse = dummy_reverse

    def tearDown(self):
        menu.reverse = self.reverse

    def test_simple(self):
        class SampleMenu(Menu):
            first_item = MenuItem('!sample')
            direct_title = MenuItem('sample', title="Some title", and_other_value='yes')

        @SampleMenu.first_item.activate
        def view(request): pass

        r = RequestLike()
        view(r)

        result = SampleMenu.build(r)
        self.assertEqual({SampleMenu.first_item}, r.active_menus)
        self.assertEqual('subitem', result['active'])
        self.assertIs(True, result['items'][0]['active'])
        self.assertIs(False, result['items'][1]['active'])
        self.assertEqual('first_item', result['items'][0]['title'])
        self.assertEqual('Some title', result['items'][1]['title'])
        self.assertEqual('yes', result['items'][1]['and_other_value'])

        self.assertEqual('sample', result['items'][0]['url'])
        self.assertEqual('route:sample', result['items'][1]['url'])

    def test_we_need_to_go_deeper(self):
        class SampleMenu(Menu):
            class SubMenu(Menu):
                item = MenuItem('sample')

            class SubMenu2(Menu):
                item = MenuItem('sample2')

                class Meta:
                    title = "Other title"
                    some_value = 42

        @SampleMenu.SubMenu2.item.activate
        @SampleMenu.SubMenu.activate
        def view(request): pass

        r = RequestLike()
        view(r)

        result = SampleMenu.build(r)

        self.assertIs(True, result['items'][0]['active'])
        self.assertEqual('subitem', result['items'][1]['active'])
        self.assertEqual('SubMenu', result['items'][0]['title'])
        self.assertEqual('Other title', result['items'][1]['title'])
        self.assertEqual(42, result['items'][1]['some_value'])

    def test_tag(self):
        class SampleMenu(Menu):
            first_item = MenuItem('sample')

        @SampleMenu.first_item.activate
        def view(request): pass

        r = RequestLike()
        view(r)

        result = render_menu({'request': r}, SampleMenu)
        self.assertEqual('first_item', result['items'][0]['title'])

    def test_caching(self):
        class SampleMenu(Menu):
            first_item = MenuItem('sample')

        SampleMenu.cache_routes()

        self.assertEqual('route:sample', SampleMenu.first_item.cached_url)
