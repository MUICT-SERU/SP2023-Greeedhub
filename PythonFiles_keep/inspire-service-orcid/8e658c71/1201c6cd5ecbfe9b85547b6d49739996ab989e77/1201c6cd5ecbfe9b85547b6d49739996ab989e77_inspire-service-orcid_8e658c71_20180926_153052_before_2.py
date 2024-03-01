# -*- coding: utf-8 -*-
from itertools import chain

from requests.models import Response

from . import exceptions, utils


class BaseOrcidClientResponse(dict):
    base_exceptions = (exceptions.TokenInvalidException,
                       exceptions.TokenMismatchException,)

    def __init__(self, memberapi, response):
        if isinstance(response, dict):
            data = response
            self.raw_response = memberapi.raw_response
        elif isinstance(response, Response):
            data = response.json()
            self.raw_response = response
        else:
            raise ValueError('response must be a dict or a requests\' Response')
        super(BaseOrcidClientResponse, self).__init__(data)

    @property
    def ok(self):
        return self.raw_response.ok

    @property
    def status_code(self):
        return self.raw_response.status_code

    @property
    def request(self):
        return self.raw_response.request

    @property
    def exceptions(self):
        return self.base_exceptions + getattr(self, 'specific_exceptions', tuple())

    def raise_for_result(self):
        """
        Check the "result" of the call. The "result" is determined not
        only by the HTTP status code, but it might also take into
        consideration the actual content of the response.
        It might raise one of the known exceptions (in self.exceptions)
        depending on the matching criteria; or it might raise
        requests.exceptions.HTTPError.
        In case of no errors no exception is raised.
        """
        for exception_class in self.exceptions:
            if exception_class.match(self):
                exception_object = exception_class(str(self))
                exception_object.raw_response = self.raw_response
                raise exception_object
        # Can raise requests.exceptions.HTTPError.
        return self.raw_response.raise_for_status()


class GetAllWorksSummaryResponse(BaseOrcidClientResponse):
    """
    A dict-like object as:
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
    specific_exceptions = (exceptions.OrcidNotFoundException,)

    def get_putcodes_for_source(self, source_client_id_path):
        for summary in chain(*utils.get_value(self, 'group.work-summary', [])):
            source_client_id_dict = utils.get_value(summary, 'source.source-client-id.path')
            putcode = summary.get('put-code')

            if not putcode or not source_client_id_dict:
                continue

            if source_client_id_dict == source_client_id_path:
                yield str(putcode)


class GetWorkDetailsResponse(BaseOrcidClientResponse):
    """
    A dict-like object as:
    {'bulk': [{'work': {'citation': {'citation-type': 'BIBTEX',
                                     'citation-value': u''},
                        'contributors': {'contributor': [{'contributor-attributes': {'contributor-role': 'AUTHOR',
                                                                                     'contributor-sequence': 'FIRST'},
                                                          'contributor-email': None,
                                                          'contributor-orcid': None,
                                                          'credit-name': {'value': 'Glashow, S.L.'}}]},
                        'country': None,
                        'created-date': {'value': 1516716146242},
                        'external-ids': {'external-id': [{'external-id-relationship': 'SELF',
                                                          'external-id-type': 'doi',
                                                          'external-id-url': {'value': 'http://dx.doi.org/10.1016/0029-5582(61)90469-2'},
                                                          'external-id-value': '10.1016/0029-5582(61)90469-2'}]},
                        'journal-title': {'value': 'Nucl.Phys.'},
                        'language-code': None,
                        'last-modified-date': {'value': 1519143190177},
                        'path': None,
                        'publication-date': {'day': None,
                                             'media-type': None,
                                             'month': None,
                                             'year': {'value': '1961'}},
                        'put-code': 912978,
                        'short-description': None,
                        'source': {'source-client-id': {'host': 'sandbox.orcid.org',
                                                        'path': 'CHANGE_ME',
                                                        'uri': 'http://sandbox.orcid.org/client/CHANGE_ME'},
                                   'source-name': {'value': 'INSPIRE-PROFILE-PUSH'},
                                   'source-orcid': None},
                        'title': {'subtitle': None,
                                  'title': {'value': 'Partial Symmetries of Weak Interactions'},
                                  'translated-title': None},
                        'type': 'JOURNAL_ARTICLE',
                        'url': {'value': 'http://labs.inspirehep.net/record/4328'},
                        'visibility': 'PUBLIC'}}]}
    """  # noqa: E501
    specific_exceptions = (exceptions.OrcidInvalidException,
                           exceptions.PutcodeNotFoundGetException,
                           exceptions.GenericGetWorksDetailsException,)


class GetBulkWorksDetailsResponse(GetWorkDetailsResponse):
    specific_exceptions = (exceptions.OrcidInvalidException,
                           exceptions.ExceedMaxNumberOfPutCodesException,
                           exceptions.PutcodeNotFoundGetException,
                           exceptions.GenericGetWorksDetailsException,)

    def get_putcodes_and_urls(self):
        for item in utils.get_value(self, 'bulk'):
            putcode = utils.get_value(item, 'work.put-code')
            url = utils.get_value(item, 'work.url.value')
            if not putcode or not url:
                continue

            yield str(putcode), url


class PostNewWorkResponse(BaseOrcidClientResponse):
    """
    A dict-like object as:
    {'location': 'http://api.orcid.org/orcid-api-web/v2.0/0000-0002-0942-3697/work/46874897'}
    """
    specific_exceptions = (exceptions.WorkAlreadyExistentException,
                           exceptions.InvalidDataException,
                           exceptions.OrcidNotFoundException,)

    def __init__(self, memberapi, response):
        try:
            data = dict(
                location=memberapi.raw_response.headers['location'],
                putcode=response,
            )
        except (KeyError, AttributeError):
            data = response
        super(PostNewWorkResponse, self).__init__(memberapi, data)


class PutUpdatedWorkResponse(BaseOrcidClientResponse):
    """
    A dict-like object as:
    {u'citation': None,
     u'contributors': {u'contributor': [{u'contributor-attributes': {u'contributor-role': u'AUTHOR',
                                                                     u'contributor-sequence': u'FIRST'},
                                         u'contributor-email': None,
                                         u'contributor-orcid': None,
                                         u'credit-name': {u'value': u'Rossoni, A.'}}]},
     u'country': None,
     u'created-date': {u'value': 1533027211637},
     u'external-ids': {u'external-id': [{u'external-id-relationship': u'SELF',
                                         u'external-id-type': u'doi',
                                         u'external-id-url': {u'value': u'http://dx.doi.org/10.1000/test.orcid.push'},
                                         u'external-id-value': u'10.1000/test.orcid.push'}]},
     u'journal-title': {u'value': u'ORCID Push test'},
     u'language-code': None,
     u'last-modified-date': {u'value': 1533027422266},
     u'path': None,
     u'publication-date': {u'day': None,
                           u'media-type': None,
                           u'month': None,
                           u'year': {u'value': u'1975'}},
     u'put-code': 46985330,
     u'short-description': None,
     u'source': {u'source-client-id': {u'host': u'orcid.org',
                                       u'path': u'0000-0001-8607-8906',
                                       u'uri': u'http://orcid.org/client/0000-0001-8607-8906'},
                 u'source-name': {u'value': u'INSPIRE-HEP'},
                 u'source-orcid': None},
     u'title': {u'subtitle': None,
                u'title': {u'value': u'ORCID Push test - New Title'},
                u'translated-title': None},
     u'type': u'JOURNAL_ARTICLE',
     u'url': {u'value': u'http://inspirehep.net/record/8201'},
     u'visibility': u'PUBLIC'}
    """
    specific_exceptions = (exceptions.OrcidNotFoundException,
                           exceptions.PutcodeNotFoundPutException,
                           exceptions.TokenWithWrongPermissionException,)

    def __init__(self, memberapi, response):
        try:
            data = memberapi.raw_response.json()
        except AttributeError:
            data = response
        super(PutUpdatedWorkResponse, self).__init__(memberapi, data)
