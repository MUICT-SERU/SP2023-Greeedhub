"""
raven_auth.py

Imports

tornado: for handling any asynchronus requests, as well as generating the HTML templates.
jupyterhub: Authenticator class as required. The BaseHandler is customised to create a custom login screen.
jinja2: Markup imported to make any custom html safe (thereby allowing a browser to render it).
raven: for producing and verifying University of Cambridge webauth requests.
ibisclient: for University of Cambridge lookup requests (to find what institution a person belongs to.
os: accessing/creating absolute filepaths for custom images
pkg_resources: for generating an absolute filepath to the raven images bundled with the plugin.

"""
from tornado import gen, web, template
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
from traitlets import Bool, Unicode, Set
from jinja2 import Markup
import raven, ibisclient
import os, pkg_resources

class CustomLoginHandler(BaseHandler):
    """
    Class which renders the login page.
    If a GET request using the variable 'next' is given, a redirect will occur after raven authentication.
    """

    next = None

    def _render(self, login_error=None, username=None, url=None, next=''):
        """
        Almost carbon copy of the JupyterHub _render method, although override with custom authenticator.
        """
        self.log.info("login url : %r", next)
        return self.render_template('login.html',
                username=username,
                login_error=login_error,
                custom_html=self.authenticator.custom_login_html(self.hub.server.base_url, next),
                login_url=url,
        )

    def get(self):
        self.next = self.get_argument('next', None, False)
        self.statsd.incr('login.request')
        login_url = self.settings['login_url']
        self.log.info("next: %r", self.next)
        if self.next:
            self.next = "?next=" + self.next
        else:
            self.next = ''

        self.finish(self._render(username=None, url=login_url, next=self.next))

    @gen.coroutine
    def post(self):
        """
        Override the BaseHandler post method.
        """
        pass

class RavenLoginHandler(BaseHandler):
    """
    Class to handle the Raven login requests.
    Upon the first visit, this Handler will create a Raven login request URL and redirect to it.
    On return (the second visit), it will process the key provided in the GET request variable 'WLS'.
    """

    wls = None
    next = None

    @gen.coroutine
    def get(self):

        # If there is a successful response from Raven, expect this to be populated.
        self.wls = self.get_argument('WLS-Response', None, False)
        self.next = self.get_argument('next', None, False)
        self.log.info("next test: %r", self.next)
        if self.wls:
            crsid = yield self.authenticator.authenticate(self, self.wls)
            if crsid and (self.authenticator.check_whitelist(crsid) or self.authenticator.check_cam_whitelist(crsid)):

                user = self.user_from_username(crsid)
                self.set_login_cookie(user)
                redirect = self.next if self.next else url_path_join(self.hub.server.base_url, 'home')
                self.redirect(redirect)
            else:
                raise web.HTTPError(401)
        else:
           # If there is no WLS-Response in the GET information, send them to login via Raven
           self.initiate_raven(self.next)

    def initiate_raven(self, next_arg):
        # Supply Raven with the information required for a redirect back to the JupyterHub server.
        protocol = 'https' if self.authenticator.ssl else 'http'
        host = self.request.host
        path = url_path_join(self.hub.server.base_url, 'raven')

        # Description sent to Raven service
        desc = self.authenticator.description

        uri = '{proto}://{host}{path}'.format(
            proto=protocol,
        	host=host,
        	path=path)

        if next_arg:
            uri = uri + "?next=" + next_arg

        self.log.info('Redirecting to Raven URI: %r', uri)
        raven_uri = raven.Request(url=uri, desc=desc).__str__()

        self.redirect(raven_uri, status=302)

class RavenAuthenticator(Authenticator):
    """
    Custom authenticator class 
    """
    # Overrides the default JupyterHub login...
    login_service = 'Raven'

    # Redirect to raven
    def login_url(self, base_url):
        return url_path_join(base_url, 'raven')

    # Configuration options
    description = Unicode(
        value = '',
    	default_value = "A JupyterHub Installation",
        config = True,
        help = "Description of the webservice to be passed to Raven."
    )
    long_description = Unicode(
        config = True,
        help = "Long description of the service being provided. Displays on login page."
    )
    login_logo = Unicode(
        config = True,
        help = "Absolute path to the logo file displayed on the login page."
    )
    inside_cudn = Bool(
        default_value = False,
        config = True,
        help = "Toggle to let the authenticator know that you are inside the CUDN, such that you can access the Lookup service."
    )
    allowed_colleges = Set(
        config = True,
        help = "A set of allowed colleges or institutions to whitelist by."
    )
    ssl = Bool(
        default_value = False,
        config = True,
        help = "SSL Configuration - used to correct the redirects (given that Tornado seems to be getting some of them wrong)."
    )

    
    def check_cam_whitelist(self, crsid):
        """
        Method which whitelists using the University Lookup service
        Your server must be within the CUDN to utilise this (If you are, activate the Authenticator's inside_cudn configuration.
        """
        if self.inside_cudn:
            if not self.allowed_colleges:
                return True
            else:
                ibis_conn = ibisclient.createConnection()
                try:
                    ibis_person_method = ibisclient.methods.PersonMethods(ibis_conn)
                    ibis_person = ibis_person_method.getPerson("crsid", crsid, "jdCollege,all_insts")

                    ibis_person_insts = []
                    for attr in ibis_person.attributes:
                        if attr.scheme == 'jdCollege':
                            ibis_person_insts.append(attr.value)
                    for inst in ibis_person.institutions:
                        ibis_person_insts.append(inst.instid)
                    # Some people belong to multiple institutions, check if any of those are in the allowed college list, if at least one is satisfied, then grant access.
                    if len(college for college in ibis_person_college if college in self.allowed_colleges) > 0:
                        return True
                except ibisclient.IbisException as e:
                    if e.get_error().status is 403:
                        self.log.info("IbisException: Status Error: %r, are you inside the CUDN?", e.get_error().status)
            return False
        else:
            return True

    # Customise the Login screen
    raven_img_path = pkg_resources.resource_filename(__name__, 'files/ravensmall.png')
    files_dir = pkg_resources.resource_filename(__name__, 'files/')

    def custom_login_html(self, login_url, next):
        raven_img_path = pkg_resources.resource_filename(__name__, 'files/ravensmall.png')
        loader = template.Loader(self.files_dir)
        html = loader.load('form.html').generate(login_logo=os.path.basename(self.login_logo),
            login_url=self.login_url(login_url),
            login_service=self.login_service,
            long_description=self.long_description,
            next=next,
            raven_img='files/raven.png')
        return Markup(html.decode("utf-8"))


    # Standard JupyterHub Authenticator class methods
    def get_handlers(self, app):
        return [
            (r'/raven?', RavenLoginHandler),
            (r'/login?', CustomLoginHandler),
            (r'/files/(.*)', web.StaticFileHandler, {'path': self.files_dir}),
            (r'/logo/(.*)', web.StaticFileHandler, {'path': os.path.dirname(self.login_logo)}),
        ]

    @gen.coroutine
    def authenticate(self, handler, data=None):
        raven_resp = raven.Response(data)
        if raven_resp.success:
            crsid = raven_resp.principal
            return crsid
        else:
            return None
