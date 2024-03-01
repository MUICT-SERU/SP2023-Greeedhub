# Jupyter
from tornado import gen, web, template
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
from traitlets import Unicode
from jinja2 import Markup

# University of Cambridge Webauth
import raven

# Accessing bundled data files
import pkg_resources

# For custom logo
import os

class CustomLoginHandler(BaseHandler):
    """Render the login page."""

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

    # Upon redirect back to login, Raven will supply get information. Store it here.
    wls = None

    @gen.coroutine
    def get(self):

        # If there is a successful response from Raven, expect this to be populated.
        self.wls = self.get_argument('WLS-Response', None, False)
        if self.wls:
            crsid = yield self.authenticator.authenticate(self, self.wls)
            if crsid:

                user = self.user_from_username(crsid)
                self.set_login_cookie(user)

                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
            else:
                raise web.HTTPError(401)
        else:
           # If there is no GET information, send them to login via Raven.
           self.initiate_raven()

    def initiate_raven(self):
        # Supply Raven with the information required for a redirect back to the jupyterhub server.
        
        protocol = self.request.protocol
        host = self.request.host
        path = url_path_join(self.hub.server.base_url, 'raven')
        
        # Description for Raven service
        desc = self.authenticator.description

        uri = '{proto}://{host}{path}'.format(
            proto=protocol,
        	host=host,
        	path=path)

        self.log.info('Redirecting to Raven URI: %r', uri)
        raven_uri = raven.Request(url=uri, desc=desc).__str__()

        self.redirect(raven_uri, status=302)

class RavenAuthenticator(Authenticator):

    # Override the default JupyterHub login...
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
    	default_value = '',
        config = True,
        help = "Long description of the service being provided. Displays on login page."
    )
    login_logo = Unicode(
        config = True,
        help = "Absolute path to the logo file displayed on the login page."
    )

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
            raven_img='files/ravensmall.png')
        return Markup(html.decode("utf-8"))

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
