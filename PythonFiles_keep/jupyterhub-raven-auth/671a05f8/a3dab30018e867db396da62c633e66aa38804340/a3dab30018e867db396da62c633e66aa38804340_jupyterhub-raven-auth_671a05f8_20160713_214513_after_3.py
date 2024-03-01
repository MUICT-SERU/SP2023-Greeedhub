# Jupyter
from tornado import gen, web, httpclient, auth
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
from traitlets import Unicode

# University of Cambridge Webauth
import raven

class RavenLoginHandler(BaseHandler):

    """
    Needs to have the get authenticated user class
    """

    wls = None

    @gen.coroutine
    def get(self):
        # If we have a successful redirect from raven
        self.wls = self.get_argument('WLS-Response', None, False)
        if self.wls:
            raven_resp = raven.Response(self.wls)
            if raven_resp.success:
                crsid = raven_resp.principal
                user = self.user_from_username(crsid)
                self.set_login_cookie(user)
                self.set_secure_cookie(user)
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
            else:
                raise web.HTTPError(401)
        else:
           self.initiate_raven()

    def initiate_raven(self):
        # Set params for url formation
        url = self.authenticator.url
        port = self.authenticator.port
        desc = self.authenticator.description

        # TODO: Utilize jupyterhub config to do this
        url = url + ":" + port +  url_path_join(self.hub.server.base_url, 'login').__str__()
        self.log.info('%r', url)
        self.log.info('Redirecting to Raven URI: %r', url)
        raven_uri = raven.Request(url=url, desc=desc).__str__()

        self.redirect(raven_uri, status=302)

class RavenAuthenticator(Authenticator):

    # Config. Fields
    url = Unicode(
        config = True,
        help = "Base url for jupyterhub"
    )
    port = Unicode(
        config = True,
        help = "Port which Jupyterhub is listening on."
    )
    description = Unicode(
        config = True,
        help = "Description of the webservice being accessed."
    )

    def get_handlers(self, app):
        return [
            (r'/login?', RavenLoginHandler)
        ]

    @gen.coroutine
    def authenticate(self, handler, data=None):
        raise NotImplementedError()
