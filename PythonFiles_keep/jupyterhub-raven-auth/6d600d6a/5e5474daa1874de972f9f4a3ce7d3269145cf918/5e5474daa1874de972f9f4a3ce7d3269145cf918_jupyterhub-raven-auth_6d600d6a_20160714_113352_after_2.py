# Jupyter
from tornado import gen, web, httpclient, auth
from jupyterhub.handlers import BaseHandler
from jupyterhub.auth import Authenticator
from jupyterhub.utils import url_path_join
from traitlets import Unicode

# University of Cambridge Webauth
import raven

class RavenLoginHandler(BaseHandler):

    wls = None

    @gen.coroutine
    def get(self):
        # If we have a successful redirect from raven
        self.wls = self.get_argument('WLS-Response', None, False)
        if self.wls:
            crsid = yield self.authenticator.authenticate(self, self.wls)
            if crsid:
                user = self.user_from_username(crsid)
                self.set_login_cookie(user)
                #self.set_secure_cookie(user)
                api_token = user.new_api_token()
                self.redirect(url_path_join(self.hub.server.base_url, 'home'))
            else:
                raise web.HTTPError(401)
        else:
           self.initiate_raven()

    def initiate_raven(self):
        # Set params for url formation
        
        protocol = self.request.protocol
        host = self.request.host
        path = url_path_join(self.hub.server.base_url, 'login')
        
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

    description = Unicode(
    	default_value = "A JupyterHub Installation",
        config = True,
        help = "Description of the webservice to be passed to Raven."
    )

    def get_handlers(self, app):
        return [
            (r'/login?', RavenLoginHandler),
            #TODO: (r'/logout', RavenLogoutHandler),
        ]

    @gen.coroutine
    def authenticate(self, handler, data=None):
        raven_resp = raven.Response(data)
        if raven_resp.success:
            crsid = raven_resp.principal
            return crsid
        else:
        	return None
