# -*- coding: utf-8 -*-
import pytest
from lxml import etree

import inspire_services.orcid.conf
from inspire_services.orcid import exceptions
from inspire_services.orcid.client import OrcidClient


class BaseTestOrcidClient(object):
    def setup(self):
        self.orcid = '0000-0002-0942-3697'  # Valid ORCID test account.
        try:
            # Pick the token from settings_local.py first.
            self.oauth_token = inspire_services.orcid.conf.settings.OAUTH_TOKENS.get(self.orcid)
        except AttributeError:
            self.oauth_token = 'mytoken'
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.putcodes = ['46674246', '46694033']


class TestGetAllWorksSummary(BaseTestOrcidClient):
    def test_happy_flow(self):
        response = self.client.get_all_works_summary()
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['group'][0]['work-summary'][0]['put-code'] == 46674246

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.get_all_works_summary()
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_token_mismatch(self):
        """
        A valid token, but related to another ORCID.
        """
        orcid = '0000-0002-6665-4934'
        self.client = OrcidClient(self.oauth_token, orcid)
        response = self.client.get_all_works_summary()
        with pytest.raises(exceptions.TokenMismatchException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.get_all_works_summary()
        with pytest.raises(exceptions.OrcidNotFoundException):
            response.raise_for_result()
        assert not response.ok

    def test_get_putcodes_for_source(self):
        orcid = '0000-0002-6665-4934'  # ATLAS author with hundreds works.
        oauth_token = inspire_services.orcid.conf.settings.OAUTH_TOKENS.get(orcid)

        self.client = OrcidClient(oauth_token, orcid)
        response = self.client.get_all_works_summary()
        response.raise_for_result()
        putcodes = response.get_putcodes_for_source('0000-0001-8607-8906')
        assert len(putcodes) == 802
        assert putcodes[0] == 43326850
        assert putcodes[-1] == 46478640


class TestGetWorksDetails(BaseTestOrcidClient):
    def test_single_putcode(self):
        response = self.client.get_works_details([self.putcodes[0]])
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['bulk'][0]['work']['put-code'] == int(self.putcodes[0])

    def test_multiple_putcodes(self):
        response = self.client.get_works_details(self.putcodes)
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['bulk'][0]['work']['put-code'] == int(self.putcodes[0])
        assert response['bulk'][1]['work']['put-code'] == int(self.putcodes[1])

    def test_too_many_putcodes(self):
        response = self.client.get_works_details([str(x) for x in range(100)])
        with pytest.raises(exceptions.ExceedMaxNumberOfPutCodesException):
            response.raise_for_result()

    def test_putcode_not_found(self):
        response = self.client.get_works_details(['xxx', self.putcodes[0]])
        with pytest.raises(exceptions.PutcodeNotFoundGetException):
            response.raise_for_result()

    def test_missing_putcode(self):
        with pytest.raises(ValueError):
            self.client.get_works_details([])

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.get_works_details(self.putcodes)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_token_mismatch(self):
        """
        A valid token, but related to another ORCID.
        """
        orcid = '0000-0002-6665-4934'
        self.client = OrcidClient(self.oauth_token, orcid)
        response = self.client.get_works_details(self.putcodes)
        with pytest.raises(exceptions.TokenMismatchException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.get_works_details(['12345'])
        with pytest.raises(exceptions.OrcidInvalidException):
            response.raise_for_result()
        assert not response.ok


class TestPostNewWork(BaseTestOrcidClient):
    work_xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <work:work xmlns:work="http://www.orcid.org/ns/work" xmlns:common="http://www.orcid.org/ns/common">
        <work:title>
            <common:title>ORCID Push test</common:title>
        </work:title>
        <work:journal-title>ORCID Push test</work:journal-title>
        <work:type>journal-article</work:type>
        <common:publication-date>
            <common:year>1975</common:year>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.1000/test.orcid.push</common:external-id-value>
                <common:external-id-url>http://dx.doi.org/10.1000/test.orcid.push</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/8201</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Rossoni, A.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """

    def setup(self):
        super(TestPostNewWork, self).setup()
        self.xml_element = etree.fromstring(self.work_xml_data.encode('utf-8'))

    def test_happy_flow(self):
        response = self.client.post_new_work(self.xml_element)
        response.raise_for_result()
        assert response.ok
        assert response['location'] == 'http://api.orcid.org/orcid-api-web/v2.0/0000-0002-0942-3697/work/46964761'
        assert response['putcode'] == '46964761'

    def test_already_existent_work(self):
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.WorkAlreadyExistentException):
            response.raise_for_result()
        assert not response.ok

    def test_missing_xml_section(self):
        title = self.xml_element.getchildren()[0]
        self.xml_element.remove(title)
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.InvalidDataException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_token_mismatch(self):
        """
        A valid token, but related to another ORCID.
        """
        orcid = '0000-0002-6665-4934'
        self.client = OrcidClient(self.oauth_token, orcid)
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.TokenMismatchException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.OrcidNotFoundException):
            response.raise_for_result()
        assert not response.ok


class TestPutUpdatedWork(BaseTestOrcidClient):
    new_title = 'ORCID Push test - New Title'
    work_xml_data = """<?xml version="1.0" encoding="UTF-8"?>
    <work:work xmlns:work="http://www.orcid.org/ns/work" xmlns:common="http://www.orcid.org/ns/common">
        <work:title>
            <common:title>{}</common:title>
        </work:title>
        <work:journal-title>ORCID Push test</work:journal-title>
        <work:type>journal-article</work:type>
        <common:publication-date>
            <common:year>1975</common:year>
        </common:publication-date>
        <common:external-ids>
            <common:external-id>
                <common:external-id-type>doi</common:external-id-type>
                <common:external-id-value>10.1000/test.orcid.push</common:external-id-value>
                <common:external-id-url>http://dx.doi.org/10.1000/test.orcid.push</common:external-id-url>
                <common:external-id-relationship>self</common:external-id-relationship>
            </common:external-id>
        </common:external-ids>
        <work:url>http://inspirehep.net/record/8201</work:url>
        <work:contributors>
            <work:contributor>
                <work:credit-name>Rossoni, A.</work:credit-name>
                <work:contributor-attributes>
                    <work:contributor-sequence>first</work:contributor-sequence>
                    <work:contributor-role>author</work:contributor-role>
                </work:contributor-attributes>
            </work:contributor>
        </work:contributors>
    </work:work>
    """.format(new_title)

    def setup(self):
        super(TestPutUpdatedWork, self).setup()
        self.xml_element = etree.fromstring(self.work_xml_data.encode('utf-8'))
        self.putcode = '46985330'

    def test_happy_flow(self):
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        response.raise_for_result()
        assert response.ok
        assert response['title']['title']['value'] == self.new_title

    def test_putcode_not_found(self):
        response = self.client.put_updated_work(self.xml_element, '77777330')
        with pytest.raises(exceptions.PutcodeNotFoundPutException):
            response.raise_for_result()
        assert not response.ok

    def test_missing_xml_section(self):
        root = etree.Element('root')
        root.append(etree.Element('child1'))
        response = self.client.post_new_work(root)
        with pytest.raises(exceptions.InvalidDataException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_token_mismatch(self):
        """
        A valid token, but related to another ORCID.
        """
        orcid = '0000-0002-6665-4934'
        self.client = OrcidClient(self.oauth_token, orcid)
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        with pytest.raises(exceptions.TokenMismatchException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        with pytest.raises(exceptions.OrcidNotFoundException):
            response.raise_for_result()
        assert not response.ok
