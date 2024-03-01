# -*- coding: utf-8 -*-
import pytest
from lxml import etree

import inspire_service_orcid.conf
from inspire_service_orcid import exceptions
from inspire_service_orcid.client import OrcidClient

from six import MovedModule, add_move  # isort:skip
add_move(MovedModule('mock', 'mock', 'unittest.mock'))
from six.moves import mock  # noqa:E402 isort:skip


class BaseTestOrcidClient(object):
    def setup(self):
        self.orcid = '0000-0002-0942-3697'  # Valid ORCID test account.
        try:
            # Pick the token from settings_local.py first.
            self.oauth_token = inspire_service_orcid.conf.settings.OAUTH_TOKENS.get(self.orcid)
        except AttributeError:
            self.oauth_token = 'mytoken'
        self.client = OrcidClient(self.oauth_token, self.orcid)
        self.putcode = '46674246'


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
        oauth_token = getattr(inspire_service_orcid.conf.settings, 'OAUTH_TOKENS', {}).get(orcid)

        self.client = OrcidClient(oauth_token, orcid)
        response = self.client.get_all_works_summary()
        response.raise_for_result()
        putcodes = list(response.get_putcodes_for_source('0000-0001-8607-8906'))
        assert len(putcodes) == 802
        assert putcodes[0] == '43326850'
        assert putcodes[-1] == '46478640'

    def test_get_putcodes_for_source_source_client_id_none(self):
        orcid = '0000-0002-4490-1930'
        token = '5b5cde05-e9f8-4aa4-9de3-de4d23f1b86a'
        self.client = OrcidClient(token, orcid)

        response = self.client.get_all_works_summary()
        response.raise_for_result()
        putcodes = list(response.get_putcodes_for_source('0000-0001-8607-8906'))
        assert len(putcodes) == 90


class TestGetWorkDetails(BaseTestOrcidClient):
    def test_happy_flow(self):
        response = self.client.get_work_details(self.putcode)
        response.raise_for_result()
        assert response.ok
        # Test only one field.
        assert response['bulk'][0]['work']['put-code'] == int(self.putcode)

    def test_putcode_not_found(self):
        response = self.client.get_work_details('xxx')
        with pytest.raises(exceptions.PutcodeNotFoundGetException):
            response.raise_for_result()

    def test_missing_putcode(self):
        with pytest.raises(ValueError):
            self.client.get_work_details(None)

    def test_invalid_token(self):
        self.client = OrcidClient('invalidtoken', self.orcid)
        response = self.client.get_work_details(self.putcode)
        with pytest.raises(exceptions.TokenInvalidException):
            response.raise_for_result()
        assert not response.ok

    def test_token_mismatch(self):
        """
        A valid token, but related to another ORCID.
        """
        orcid = '0000-0002-6665-4934'
        self.client = OrcidClient(self.oauth_token, orcid)
        response = self.client.get_work_details(self.putcode)
        with pytest.raises(exceptions.TokenMismatchException):
            response.raise_for_result()
        assert not response.ok

    def test_invalid_orcid(self):
        self.client = OrcidClient(self.oauth_token, 'INVALID-ORCID')
        response = self.client.get_work_details('12345')
        with pytest.raises(exceptions.OrcidInvalidException):
            response.raise_for_result()
        assert not response.ok


class TestGenerateGetBulkWorksDetails(object):
    def setup(self):
        self.putcodes = ['43326850', '43255490', '43183518', '43857637', '43257979', '43938460', '43553536', '43846642', '43869107', '43466717', '43880082', '43852910', '44762573', '44762737', '44762744', '44762721', '44762617', '43257122', '43861964', '43938538', '43606530', '43855125', '44762615', '44762741', '43554289', '44762570', '44762735', '44762597', '43859780', '43941962', '43856818', '43938515', '43864453', '43875319', '43935537', '43467792', '44077351', '43554306', '44472652', '43911727', '43922432', '43916436', '43907796', '43924927', '43923874', '43938553', '43938542', '43878004', '43935695', '43881622', '43935569', '44231173', '43880802', '43938523', '43938458', '43935897', '43919253', '43918420', '43938697', '43920855', '43933388', '43942717', '43910178', '44515789', '43882441', '43935355', '43935418', '43935500', '43929711', '43935348', '43938613', '43919864', '43885354', '43935660', '43882622', '43935419', '43935519', '43942195', '43935682', '43949957', '43941870', '43938614', '43938644', '43941852', '43935478', '43937005', '44216033', '43948457', '43942230', '43938670', '43935725', '43942117', '43935577', '44227246', '43942042', '44219584', '43942229', '43942467', '43935574', '43461438', '43939244', '43942225', '43942110', '44218042', '44236863', '43942221', '43935690', '43938687', '43942306', '43326714', '43935600', '43935671', '43935595', '44229237', '43942579', '43935727', '43939389', '43935714', '44232896', '44227649', '43935744', '43938719', '43938710', '43942556', '44237648', '44226428', '43938991', '44236016', '43935746', '44236622', '43938809', '44234262', '43942562', '43939267', '43935804', '43935814', '44235446', '44238589', '43476255', '44238117', '43942245', '43935831', '44255508', '43935773', '43935525', '43349513', '43939364', '43942333', '44259358', '43334280', '43935879', '43474664', '43942483', '43868647', '43942582', '44269186', '43935857', '43939273', '44265932', '43328661', '43939436', '44575020', '44252784', '43473085', '43935955', '43329599', '43474084', '43942511', '43935852', '43325385', '43935788', '43942608', '43935829', '43942738', '43935875', '43939367', '44274797', '43328989', '43474829', '43942339', '43330602', '43939455', '43939372', '43943050', '43351389', '43328159', '43329373', '43935762', '43939467', '43943007', '43476291', '44272682', '43478322', '43343506', '43483181', '43347500', '43333264', '43858017', '43473511', '43332255', '43476010', '43350059', '44251364', '43475852', '43353967', '43849619', '43819343', '43339682', '43348858', '43333748', '44217143', '44232508', '43822751', '43939441', '43339402', '44284285', '43478099', '43356509', '43942969', '43348252', '43483990', '43936102', '43939877', '43935994', '44575015', '43939643', '44285709', '43352429', '43942965', '43364988', '44265579', '43939719', '43940213', '43368521', '43939725', '43361294', '43936167', '43293661', '43362128', '43940188', '43358238', '43936143', '44283137', '44284877', '43356836', '43939941', '44293857', '43363375', '43361159', '43365921', '43939949', '43941280', '43368183', '44291548', '43360300', '43366583', '43936275', '43370435', '43939860', '43361521', '43936314', '43942905', '43942981', '43292406', '43367691', '44317462']  # noqa: E501
        self.orcid = '0000-0002-6665-4934'  # ATLAS author.
        try:
            # Pick the token from settings_local.py first.
            self.oauth_token = inspire_service_orcid.conf.settings.OAUTH_TOKENS.get(self.orcid)
        except AttributeError:
            self.oauth_token = 'mytoken'
        self.client = OrcidClient(self.oauth_token, self.orcid)

    def test_happy_flow(self):
        for response in self.client.generate_get_bulk_works_details(self.putcodes):
            response.raise_for_result()
            assert response.ok
            assert str(response['bulk'][0]['work']['put-code']) in self.putcodes
            assert str(response['bulk'][-1]['work']['put-code']) in self.putcodes

    def test_too_many_putcodes(self):
        from inspire_service_orcid import client
        with mock.patch.object(client, 'MAX_PUTCODES_PER_WORKS_DETAILS_REQUEST', 101):
            for response in self.client.generate_get_bulk_works_details([str(x) for x in range(101)]):
                with pytest.raises(exceptions.ExceedMaxNumberOfPutCodesException):
                    response.raise_for_result()

    def test_get_putcodes_and_urls(self):
        for response in self.client.generate_get_bulk_works_details(self.putcodes):
            response.raise_for_result()
            assert response.ok
            putcodes_and_urls = list(response.get_putcodes_and_urls())
            # Note: the recorded cassette returns the same result for each for loop.
            assert putcodes_and_urls[0] == ('43183518', 'http://inspirehep.net/record/1665234')
            assert putcodes_and_urls[-1] == ('44227246', 'http://inspirehep.net/record/1515025')


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
        assert response['putcode'] == 46964761

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

    def test_generic_400(self):
        response = self.client.post_new_work(self.xml_element)
        with pytest.raises(exceptions.Generic400Exception):
            response.raise_for_result()
        assert not response.ok

    def test_external_identifier_required(self):
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
        xml_element = etree.fromstring(work_xml_data.encode('utf-8'))
        response = self.client.post_new_work(xml_element)
        with pytest.raises(exceptions.ExternalIdentifierRequiredException):
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
        assert response['putcode'] == int(self.putcode)

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

    def test_token_with_wrong_permission(self):
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        with pytest.raises(exceptions.TokenWithWrongPermissionException):
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

    def test_duplicated_external_identifier(self):
        response = self.client.put_updated_work(self.xml_element, self.putcode)
        with pytest.raises(exceptions.DuplicatedExternalIdentifierException):
            response.raise_for_result()
        assert not response.ok

    def test_external_identifier_required(self):
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
        """.format(self.new_title)
        xml_element = etree.fromstring(work_xml_data.encode('utf-8'))
        response = self.client.put_updated_work(xml_element, self.putcode)
        with pytest.raises(exceptions.ExternalIdentifierRequiredException):
            response.raise_for_result()
        assert not response.ok
