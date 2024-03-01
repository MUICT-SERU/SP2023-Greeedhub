# -*- coding: utf-8 -*-
from orcid import MemberAPI
from requests.exceptions import HTTPError
from time_execution import time_execution

from inspire_service_orcid.conf import settings

from . import models, utils

MAX_PUTCODES_PER_WORKS_DETAILS_REQUEST = 100


class OrcidClient(object):
    accept_json = 'application/orcid+json'
    accept_xml = 'application/orcid+xml'

    def __init__(self, oauth_token, orcid):
        self.oauth_token = oauth_token
        self.orcid = orcid
        self.memberapi = MemberAPI(
            settings.CONSUMER_KEY,
            settings.CONSUMER_SECRET,
            settings.DO_USE_SANDBOX,
            timeout=settings.REQUEST_TIMEOUT,
            do_store_raw_response=True)

    @time_execution
    def get_all_works_summary(self):
        """
        Get a summary of all works for the given orcid.
        GET http://api.orcid.org/v2.0/0000-0002-0942-3697/works
        """
        try:
            response = self.memberapi.read_record_member(
                orcid_id=self.orcid,
                request_type='works',
                token=self.oauth_token,
                accept_type=self.accept_json,
            )
        except HTTPError as exc:
            response = exc.response
        return models.GetAllWorksSummaryResponse(self.memberapi, response)

    @time_execution
    def get_work_details(self, putcode):
        """
        Get a summary of a work for the given orcid.
        GET https://api.orcid.org/v2.0/0000-0002-0942-3697/works/46674246

        Args:
            putcode (string): putcode.
        """
        if not putcode:
            raise ValueError('putcode required')
        try:
            response = self.memberapi.read_record_member(
                orcid_id=self.orcid,
                request_type='works',
                token=self.oauth_token,
                accept_type=self.accept_json,
                put_code=[putcode],
            )
        except HTTPError as exc:
            response = exc.response
        return models.GetWorkDetailsResponse(self.memberapi, response)

    @time_execution
    def _get_bulk_works_details(self, putcodes):
        """
        Get a summary of the given works for the given orcid.
        GET https://api.orcid.org/v2.0/0000-0002-0942-3697/works/46674246

        Args:
            putcode (List[string]): putcode.

        Yields:
            GetWorksDetailsResponse: the response.

        Docs: https://members.orcid.org/api/tutorial/read-orcid-records#usetoken

        """
        if not putcodes:
            raise ValueError('putcode required')
        if len(putcodes) > MAX_PUTCODES_PER_WORKS_DETAILS_REQUEST:
            raise ValueError('Too many putcodes ({}), max={}'.format(
                len(putcodes), MAX_PUTCODES_PER_WORKS_DETAILS_REQUEST
            ))
        try:
            response = self.memberapi.read_record_member(
                orcid_id=self.orcid,
                request_type='works',
                token=self.oauth_token,
                accept_type=self.accept_json,
                put_code=putcodes,
            )
        except HTTPError as exc:
            response = exc.response
        return models.GetBulkWorksDetailsResponse(self.memberapi, response)

    def get_bulk_works_details_iter(self, putcodes):
        """
        Yield a summary of the given works for the given orcid.
        A number of requests:
        GET https://api.orcid.org/v2.0/0000-0002-0942-3697/works/46674246

        Args:
            putcode (List[string]): putcode.

        Yields:
            GetWorksDetailsResponse: the response.

        Note:
            This call can be very expensive for an author with many works (if
            each work also has many contributors). Fi. for an ATLAS author with
            ~750 works, 8 calls would be performed with a total data transfer
            > 0.5 Gb.

        Docs: https://members.orcid.org/api/tutorial/read-orcid-records#usetoken
        """
        if not putcodes:
            raise ValueError('putcodes can not be an empty sequence')

        # Split the sequence in batches of 100 putcodes.
        for putcodes_chunk in utils.chunked_sequence(putcodes, MAX_PUTCODES_PER_WORKS_DETAILS_REQUEST):
            yield self._get_bulk_works_details(putcodes_chunk)

    @time_execution
    def post_new_work(self, xml_element):
        """
        Create a new work for the given orcid and with the given xml data.
        POST https://api.orcid.org/v2.0/0000-0002-0942-3697/work

        Args:
            xml_element (lxml.etree._Element): work data in xml format.
        """
        if xml_element is None:
            raise ValueError('xml_element cannot be None')
        try:
            response = self.memberapi.add_record(
                orcid_id=self.orcid,
                token=self.oauth_token,
                request_type='work',
                data=xml_element,
                content_type=self.accept_xml,
            )
        except HTTPError as exc:
            response = exc.response
        return models.PostNewWorkResponse(self.memberapi, response)

    @time_execution
    def put_updated_work(self, xml_element, putcode):
        """
        Update en existent work.
        PUT https://api.orcid.org/v2.0/0000-0002-0942-3697/work/46985330

        Args:
            xml_element (lxml.etree._Element): work data in xml format.
            putcode (string): work's putcode.
        """
        if not putcode:
            raise ValueError('putcode cannot be empty')
        if xml_element is None:
            raise ValueError('xml_element cannot be None')

        try:
            response = self.memberapi.update_record(
                orcid_id=self.orcid,
                token=self.oauth_token,
                request_type='work',
                data=xml_element,
                put_code=putcode,
                content_type=self.accept_xml,
            )
        except HTTPError as exc:
            response = exc.response
        return models.PutUpdatedWorkResponse(self.memberapi, response)

    @time_execution
    def delete_work(self, putcode):
        """
        Delete en existent work.
        DELETE https://api.orcid.org/v2.0/0000-0002-0942-3697/work/46985330

        Args:
            putcode (string): work's putcode.
        """
        if not putcode:
            raise ValueError('putcode cannot be empty')

        try:
            response = self.memberapi.remove_record(
                orcid_id=self.orcid,
                token=self.oauth_token,
                request_type='work',
                put_code=putcode,
            )
        except HTTPError as exc:
            response = exc.response
        return models.DeleteWorkResponse(self.memberapi, response)
