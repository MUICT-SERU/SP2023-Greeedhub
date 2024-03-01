import os
from unittest import TestCase
import pytest

from ..saddlebag import Saddlebag
from ..exceptions import (
    DuplicateConfigurationFile,
    MalformedConfigurationFile)


@pytest.fixture()
def setup_environment():
    test_file_path = os.path.dirname(__file__)
    os.environ['JSON_CONFIGURATION_FILES'] = test_file_path + '/json'
    os.environ['INVALID_JSON_FILES'] = test_file_path + '/invalid-json'
    os.environ['SINGLE_DOCUMENT_YAML_FILES'] = test_file_path + '/single-yaml'
    os.environ['MULTI_DOCUMENT_YAML_FILES'] = test_file_path + '/multi-document-yaml'
    os.environ['INVALID_YAML_FILES'] = test_file_path + '/invalid-yaml'
    os.environ['DUPLICATE_CONFIGURATION_FILES'] = test_file_path + '/duplicates'
    os.environ['MISC_FILES'] = test_file_path + '/misc-files'
    os.environ['INVALID_LOCATION'] = test_file_path + '/non-existent'


@pytest.mark.usefixtures('setup_environment')
class TestSaddlebag(TestCase):
    """
    Exercises the functionality of the Saddlebag class.
    """
    def test_init_loading_of_environment(self):
        """
        The Saddlebag object constructor will load environment variables
        onto the `env` object attribute but NOT using element access notation.
        """
        saddlebag = Saddlebag()
        assert saddlebag.env == os.environ
        assert saddlebag['env'] is None

    def test_init_with_invalid_environment_variables(self):
        """
        Instance creation fails if non-existent environment variables
        are passed into the constructor.
        """
        with pytest.raises(ValueError):
            Saddlebag(['NON_EXISTENT_ENV_VAR'])

    def test__configuration_files(self):
        """
        Saddlebag._configuration_files returns references to all supported
        configuration files.

        In other words, it ignores unsupported file types.
        """
        saddlebag = Saddlebag()
        configuration_files = saddlebag._configuration_files(
            ['JSON_CONFIGURATION_FILES',
             'SINGLE_DOCUMENT_YAML_FILES',
             'MISC_FILES'])
        assert len(configuration_files) == 2

    def test__check_for_name_collision(self):
        """
        If two configuration files have the same name (this does not include
        the file extension), an error will be raised when attempting to
        initialize the object.
        """
        with pytest.raises(DuplicateConfigurationFile):
            Saddlebag(
                ['JSON_CONFIGURATION_FILES',
                 'DUPLICATE_CONFIGURATION_FILES'])

    def test__load_data_onto_attributes(self):
        """
        Validate that a Saddlebag object's data matches
        loaded configuration files.
        """

        saddlebag = Saddlebag(['JSON_CONFIGURATION_FILES',
                               'SINGLE_DOCUMENT_YAML_FILES'])

        assert saddlebag['smtp-settings']['TestAccount1'] == dict(
            url='smtp.yourschool.edu',
            login='testaccount1',
            password='testaccount1password')

        assert saddlebag['ldap'] == {
            "primary": {
                "url": "ldaps://primaryldap.example.edu:111",
                "login": "cn=LDAP Testing",
                "password": "LDAP Password"}}

        saddlebag = Saddlebag(['MULTI_DOCUMENT_YAML_FILES'])

        assert len(saddlebag['email']) == 3
        assert saddlebag['email'][0]['Thomas'] == {'addresses': ['thomas-is-great@example.com']}
        assert saddlebag['email'][1]['Newt'] == {'addresses': ['newt-is-great@example.com']}
        assert saddlebag['email'][2]['Minho'] == {'addresses': ['minho-is-great@example.com']}

    def test__load_data_onto_attributes_with_malformed_json_files(self):
        """
        `_load_data_onto_attribute` will raise a
        MalformedConfigurationFile exception if a JSON
        configuration file is found to have syntax errors.
        """
        with pytest.raises(MalformedConfigurationFile):
            Saddlebag(['INVALID_JSON_FILES'])

    def test__load_data_onto_attributes_with_malformed_yaml_files(self):
        """
        `_load_data_onto_attribute` will raise a
        MalformedConfigurationFile exception if a YAML
        configuration file is found to have syntax errors.
        """
        with pytest.raises(MalformedConfigurationFile):
            Saddlebag(['INVALID_YAML_FILES'])

    def test_object_iterability(self):
        """You can iterate a Saddlebag object."""

        saddlebag = Saddlebag(['JSON_CONFIGURATION_FILES',
                               'SINGLE_DOCUMENT_YAML_FILES'])
        for _ in saddlebag:
            pass

    def test_object_deletion_mutability(self):
        """You can delete items from a Saddlebag object."""

        saddlebag = Saddlebag(['JSON_CONFIGURATION_FILES',
                               'SINGLE_DOCUMENT_YAML_FILES'])
        assert saddlebag['ldap']
        del saddlebag['ldap']
        assert saddlebag['ldap'] is None

    def test_object_len(self):
        """
        Using `len()` on a Saddlebag object will get you the number of
        top level elements keys currently present.
        """
        saddlebag = Saddlebag(['JSON_CONFIGURATION_FILES',
                               'SINGLE_DOCUMENT_YAML_FILES'])
        assert len(saddlebag) == 2

    def test_object_repr(self):
        """
        Using `repr()` or `print()` on a Saddlebag object will
        will return it's internal `_data` dictionary.
        """
        saddlebag = Saddlebag(['JSON_CONFIGURATION_FILES',
                               'SINGLE_DOCUMENT_YAML_FILES'])
        assert repr(saddlebag) == (
            "{'ldap': {'primary': {'url': 'ldaps://primaryldap.example.edu:111', "
            "'login': 'cn=LDAP Testing', 'password': 'LDAP Password'}}, "
            "'smtp-settings': {'TestAccount1': {'url': 'smtp.yourschool.edu', "
            "'login': 'testaccount1', 'password': 'testaccount1password'}}}")