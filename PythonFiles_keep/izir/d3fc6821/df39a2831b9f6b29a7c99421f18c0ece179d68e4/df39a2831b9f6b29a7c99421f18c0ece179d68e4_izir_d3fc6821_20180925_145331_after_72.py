"""An example of using a middleware to require HTTPS connections.
    requires https://github.com/falconry/falcon-require-https to be installed via
    pip install falcon-require-https
"""
import izi
from falcon_require_https import RequireHTTPS

izi.API(__name__).http.add_middleware(RequireHTTPS())


@izi.get()
def my_endpoint():
    return 'Success!'
