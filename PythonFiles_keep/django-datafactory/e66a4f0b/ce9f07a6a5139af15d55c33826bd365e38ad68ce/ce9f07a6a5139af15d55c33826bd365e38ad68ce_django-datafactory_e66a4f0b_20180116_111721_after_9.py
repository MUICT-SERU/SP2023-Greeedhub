from __future__ import unicode_literals

import base64
import json
import logging
import os
import sys
from urllib import quote

from django.conf import settings

from django_datafactory import settings as django_datafactory_settings

try:
    # For Python 3.0 and later
    from urllib.error import HTTPError
    from urllib.request import urlopen
    from urllib.request import Request
except ImportError:
    # Fall back to Python 2's urllib2
    from urllib2 import HTTPError, Request, urlopen


class DataFactoryWrapper(object):
    interface_version = 'django_datafactory_v{}'.format(django_datafactory_settings.DJANGO_DATAFACTORY_VERSION)
    cafile = os.path.join(os.path.abspath(os.path.join(os.path.abspath(os.path.dirname(os.path.dirname(__file__))), 'django_datafactory')), 'cacert.pem')

    api_url = django_datafactory_settings.DATAFACTORY_API_URL

    auth = None

    def __init__(self, auth=None):
        super(DataFactoryWrapper, self).__init__()
        if getattr(settings, 'DATAFACTORY', False):
            self.auth = auth

    def autocomplete(self, uuid=None, postal_code=None, city=None, district=None, street=None):

        response = self.typeahead(uuid=uuid, postal_code=postal_code, city=city, district=district, street=street)

        if type(response['Ergebnisse']) is dict:
            if type(response['Ergebnisse']) is not dict and type(response['Ergebnisse']) is not list:
                result = None
            elif type(response['Ergebnisse']['Ergebnis']) is list:
                result = response['Ergebnisse']['Ergebnis'][0]
            else:
                result = response['Ergebnisse']['Ergebnis']
        else:
            result = None
        return result

    def typeahead(self, uuid=None, postal_code=None, city=None, district=None, street=None):

        if not self.auth:
            return False

        data = []
        if uuid:
            url = u'/autocomplete/de/select/'
            data.append('uuid={}'.format(postal_code))
        else:
            url = u'/autocomplete/de/search/'

        if postal_code:
            url += 'Plz'
            data.append(u'plz={}'.format(postal_code))
        if city:
            url += 'Ort'
            data.append(u'ort={}'.format(quote(city.encode('utf8'))))
        if district:
            url += 'Otl'
            data.append(u'otl={}'.format(quote(district.encode('utf8'))))
        if street:
            url += 'Str'
            data.append(u'str={}'.format(quote(street.encode('utf8'))))
        data_str = u"&".join(data)
        url += u"?" + data_str
        response = self.call_api(url=url)
        return response

    def call_api(self, url=None, data=None):
        if not self.auth:
            return False
        if not url.lower().startswith('http'):
            url = '{0}{1}'.format(self.api_url, url)
        request = Request(url)
        base64string = base64.encodestring('%s:%s' % (self.auth['API_USERNAME'], self.auth['API_PASSWORD'])).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        if data:
            data = json.dumps(data)
            data_len = len(data)
            request.add_header('Content-Length', data_len)
            request.data = data.encode(encoding='utf-8')
        elif data == '':
            request.method = 'POST'
            request.data = ''.encode(encoding='utf-8')
        request.add_header('Content-Type', 'application/json')
        request.add_header('Accept', 'application/json')
        try:
            if sys.version_info.major > 2 or (sys.version_info.major == 2 and sys.version_info.major > 7 or (sys.version_info.major == 7 and sys.version_info.major >= 9)):
                response = urlopen(request, cafile=self.cafile)
            else:
                response = urlopen(request)
        except HTTPError as e:
            logger = logging.getLogger(__name__)
            fp = e.fp
            body = fp.read()
            fp.close()
            if hasattr(e, 'code'):
                logger.error("Datafactory Error {0}({1}): {2}".format(e.code, e.msg, body))
            else:
                logger.error("Datafactory Error({0}): {1}".format(e.msg, body))
        else:
            return json.loads(response.read().decode('utf-8'))
        return False
