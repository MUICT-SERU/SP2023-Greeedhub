import unittest
from css_html_js_minify.html_minifier import remove_html_comments

class Test_Html_Minifier(unittest.TestCase):
    def test_remove_html_comments(self):
        html_in = '<p>This is a test</p><!-- Begone -->'
        html_out = '<p>This is a test</p>'

        self.assertEqual(remove_html_comments(html_in), html_out)

if __name__ == '__main__':
    unittest.main()