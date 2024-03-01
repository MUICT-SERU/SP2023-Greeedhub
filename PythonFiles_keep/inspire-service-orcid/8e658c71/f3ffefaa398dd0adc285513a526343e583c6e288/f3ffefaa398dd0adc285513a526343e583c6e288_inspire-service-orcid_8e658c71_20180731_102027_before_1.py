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
        """
        try:
            response = self.memberapi.read_record_member(
                self.orcid,
                'works',
                self.oauth_token,
                accept_type='application/orcid+json',
            )
        except HTTPError as exc:
            response = exc.response
        return models.GetAllWorksSummaryResponse(self.memberapi, response)

    def get_works_details(self, putcodes):
        """
        Get a summary of all works for the given orcid.
        GET https://api.orcid.org/v2.0/0000-0002-0942-3697/works/46674246,46694033
        """
        if not putcodes:
            raise ValueError('pucodes cannot be an empty sequence')
        try:
            response = self.memberapi.read_record_member(
                self.orcid,
                'works',
                self.oauth_token,
                accept_type='application/orcid+json',
                put_code=putcodes,
            )
        except HTTPError as exc:
            response = exc.response
        return models.GetWorksDetailsResponse(self.memberapi, response)
