# -*- coding: utf-8 -*-
from orcid import MemberAPI
from requests.exceptions import HTTPError

from inspire_services.orcid.conf import settings

from . import models


class OrcidClient(object):
    def __init__(self, oauth_token, orcid):
        self.oauth_token = oauth_token
        self.orcid = orcid
        self.memberapi = MemberAPI(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.DO_USE_SANDBOX,
            timeout=settings.REQUEST_TIMEOUT,
            do_store_raw_response=True)

    def get_all_works_summary(self):
        """
        Get a summary of all works for the given orcid.
        GET http://api.orcid.org/v2.0/0000-0002-0942-3697/works

        Returns: in case of success, a dict-like object as:
            {'group': [{'external-ids': {'external-id': [{'external-id-relationship': 'SELF',
                                                          'external-id-type': 'doi',
                                                          'external-id-url': {'value': 'http://dx.doi.org/10.1000/test.orcid.push'},
                                                          'external-id-value': '10.1000/test.orcid.push'}]},
                        'last-modified-date': {'value': 1531817559038},
                        'work-summary': [{'created-date': {'value': 1531150299725},
                                          'display-index': '0',
                                          'external-ids': {'external-id': [{'external-id-relationship': 'SELF',
                                                                            'external-id-type': 'doi',
                                                                            'external-id-url': {'value': 'http://dx.doi.org/10.1000/test.orcid.push'},
                                                                            'external-id-value': '10.1000/test.orcid.push'}]},
                                          'last-modified-date': {'value': 1531817559038},
                                          'path': '/0000-0002-0942-3697/work/46394300',
                                          'publication-date': None,
                                          'put-code': 46394300,
                                          'source': {'source-client-id': {'host': 'orcid.org',
                                                                          'path': '0000-0001-8607-8906',
                                                                          'uri': 'http://orcid.org/client/0000-0001-8607-8906'},
                                                     'source-name': {'value': 'INSPIRE-HEP'},
                                                     'source-orcid': None},
                                          'title': {'subtitle': None,
                                                    'title': {'value': 'Some Results Arising from the Study of ORCID push in QA at ts 1531817555.38'},
                                                    'translated-title': None},
                                          'type': 'JOURNAL_ARTICLE',
                                          'visibility': 'PUBLIC'}]}],
             'last-modified-date': {'value': 1531817559038},
             'path': '/0000-0002-0942-3697/works'}
        """  # noqa: E501
        try:
            response = self.memberapi.read_record_member(
                self.orcid,
                'works',
                self.oauth_token,
                accept_type='application/orcid+json',
            )
        except HTTPError as exc:
            response = exc.response
        return models.BaseOrcidClientResponse(self.memberapi, response)
