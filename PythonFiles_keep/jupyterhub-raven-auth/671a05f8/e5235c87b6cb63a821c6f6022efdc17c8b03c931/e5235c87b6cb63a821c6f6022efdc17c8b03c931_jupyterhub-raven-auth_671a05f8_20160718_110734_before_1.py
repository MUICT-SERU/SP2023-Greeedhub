# Jupyter
from tornado import gen, web, template
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
from traitlets import Bool, Unicode, Set
from jinja2 import Markup

# University of Cambridge Webauth
import raven

# Accessing bundled data files
import pkg_resources

# Access absolute paths for custom images
import os

# Ibis - College lookup
import ibisclient

class CustomLoginHandler(BaseHandler):
    """Render the login page."""
    # TODO: Think about moving the custom_html method here
    # Almost carbon copy of the JupyterHub _render method, although override with custom authenticator.
    def _render(self, login_error=None, username=None):
        return self.render_template('login.html',
                next='',
                username=username,
                login_error=login_error,
                custom_html=self.authenticator.custom_login_html(self.hub.server.base_url),
                login_url=self.settings['login_url'],
        )

    def get(self):
        self.statsd.incr('login.request')
        self.finish(self._render(username=None))

    @gen.coroutine
    def post(self):
        pass


class RavenLoginHandler(BaseHandler):

    # Once redirected back to the login, Raven will supply a key in the WLS-Response GET argument.
    wls = None

    @gen.coroutine
    def get(self):

        # If there is a successful response from Raven, expect this to be populated.
        self.wls = self.get_argument('WLS-Response', None, False)
        if self.wls:
            crsid = yield self.authenticator.authenticate(self, self.wls)
            if crsid and self.authenticator.check_cam_whitelist(crsid):

                user = self.user_from_username(crsid)
                self.set_login_cookie(user)
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
            else:
                raise web.HTTPError(401)
        else:
           # If there is no GET information, send them to login via Raven.
           self.initiate_raven()

    def initiate_raven(self):
        # Supply Raven with the information required for a redirect back to the JupyterHub server.

        protocol = self.request.protocol
        host = self.request.host
        path = url_path_join(self.hub.server.base_url, 'raven')

        # Description sent to Raven service
        desc = self.authenticator.description

        uri = '{proto}://{host}{path}'.format(
            proto=protocol,
        	host=host,
        	path=path)

        self.log.info('Redirecting to Raven URI: %r', uri)
        raven_uri = raven.Request(url=uri, desc=desc).__str__()

        self.redirect(raven_uri, status=302)

class RavenAuthenticator(Authenticator):

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
        help = "(Not implemented yet)."
    )

    # University Lookup service
    # Your server must be within the CUDN to utilise this.
    def check_cam_whitelist(self, crsid):
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

    def custom_login_html(self, login_url):
        raven_img_path = pkg_resources.resource_filename(__name__, 'files/ravensmall.png')
        loader = template.Loader(self.files_dir)
        html = loader.load('form.html').generate(login_logo=os.path.basename(self.login_logo),
            login_url=self.login_url(login_url),
            login_service=self.login_service,
            long_description=self.long_description,
            raven_img='files/raven.png')
        return Markup(html.decode("utf-8"))


    # Standard JupyterHub Authenticator class methods
    def get_handlers(self, app):
        return [
            (r'/raven?', RavenLoginHandler),
            (r'/login', CustomLoginHandler),
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
