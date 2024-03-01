from mechanize import Browser
from lxml import html

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
        return msg in self.tree().xpath('string()')

    def tree(self):
        return html.fromstring(self.response().read())

    def select_form_by_id(self, idname):
        formcount = 0
        for frm in self.forms():
            if str(frm.attrs["id"])==idname:
                break
            formcount += 1
        return self.select_form(nr=formcount)

