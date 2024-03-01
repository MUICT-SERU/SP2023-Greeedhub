import logging
import sys
from mechanize import Browser
from lxml import html

_log = logging.getLogger(__name__)
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

class BrowserPlus(Browser):

    def __init__(self):
        Browser.__init__(self)
        self.set_handle_robots(False)
        self.addheaders = [('Accept',
            'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')]
        
    def contains(self, msg):
        """This returns true if the string provided in msg is contained in the
        browsers current page.
        """
        return msg in self._tree().xpath('string()')

    def _tree(self):
        return html.fromstring(self.response().read())

    def select_form_by(self, attr, search):
        formcount = 0
        for frm in self.forms():
            if str(frm.attrs[attr]) == search:
                break
            formcount += 1
        return self.select_form(nr=formcount)
   
    def get(self, css):
        """Returns the first occurence of an element matching the css selector
        if it exists and None otherwise
        """
        e = self.get_all(css)
        if e:
            return e[0]
        return None

    def get_all(self, css):
        """Returns a list of all elements that match the css selector
        """
        return self._tree().cssselect(css)

    def go(self, text):
        try:
            return self.follow_link(text_regex=text)
        except:
            _log.error("Can't find link with text '%s'" % text)
            return None
