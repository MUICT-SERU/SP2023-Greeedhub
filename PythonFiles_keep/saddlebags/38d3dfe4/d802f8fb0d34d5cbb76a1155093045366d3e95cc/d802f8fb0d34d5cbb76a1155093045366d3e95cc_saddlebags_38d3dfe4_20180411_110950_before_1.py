import json
import glob
import os
import re
import collections

import yaml
from yaml.parser import ParserError, ScannerError

from saddlebags import exceptions


SUPPORTED_FILE_TYPES = ['json', 'yaml', 'yml']


class Saddlebag(collections.MutableMapping):
    """
    Provides access to the contents of JSON/YAML configuration
    files and environment variables using standard object or dictionary
    style syntax.
    """

    def __init__(self, configuration_locations: list=None):
        """
        The constructor creates an top-level element on the object for each
        configuration file found in the directories specified by
        a list of environment variables.

        Additionally, all read/write access to environment variables
        is available via the `env` object attribute.

        Args:
            configuration_locations: List of environment variables
                which point to directories containing configuration files.
        """
        self.env = os.environ
        self._data = dict()
        if not configuration_locations:
            configuration_locations = []

        configuration_files = (
            self._configuration_files(configuration_locations))

        for configuration_file in configuration_files:
            key_name = re.search(
                r"([-_A-Za-z0-9]+)\.(json|yaml|yml|conf)",
                configuration_file).group(1)

            self._check_for_name_collision(key_name)
            self._load_data_onto_attribute(key_name, configuration_file)

    def __getitem__(self, key: str):
        return self._data.get(key.lower())

    def __setitem__(self, key: str, value):
        self._data[key.lower()] = value

    def __delitem__(self, key):
        del self._data[key.lower()]

    def __iter__(self):
        return iter(self._data)

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return str(self._data)

    def _configuration_files(self, config_files_locations):
        """
        Identify all configuration files in a given location.

        Returns:
            A list containing paths to configuration files.

        Raises:
            ValueError: When a non-existent ENV_VAR is referenced.
        """
        configuration_files = list()
        for location in config_files_locations:
            try:
                configuration_files.extend(
                    [file for file in glob.glob(os.environ[location] + '/*')
                     if file.rpartition('.')[2] in SUPPORTED_FILE_TYPES])
            except KeyError:
                raise ValueError(
                    'The environment variable specified '
                    'by the client ({}) for use by '
                    'the constructor does not exist '
                    'on the system.'.format(location))
        return configuration_files

    def _check_for_name_collision(self, key):
        """
        Ensure that a given element key is not already present on the
        object.

        Args:
            key: The key to evaluate.

        Raises:
             DuplicationConfigurationFile: If another configuration file
                of the same name has already been loaded onto the file.
        """
        if self[key]:
            raise exceptions.DuplicateConfigurationFile(
                "Two configuration files share the following name "
                "{}.  This is not allowed.".format(key))

    def _load_data_onto_attribute(self, attribute_name, configuration_file):
        with open(configuration_file) as configuration_data:
            file_extension = configuration_file.partition('.')[2].lower()

            # JSON Loading
            if file_extension == 'json':
                try:
                    self.update(
                        {attribute_name: json.load(configuration_data)})
                except ValueError:
                    raise exceptions.MalformedConfigurationFile(
                        "The configuration file, {}, contains "
                        "syntax errors.".format(configuration_file))

            # YAML Loading
            elif file_extension in ['yaml', 'yml']:
                try:
                    results = list(yaml.load_all(configuration_data))
                except (ParserError, ScannerError):
                    raise exceptions.MalformedConfigurationFile(
                        "The configuration file, {}, contains "
                        "syntax errors.".format(configuration_file))
                else:
                    if len(results) > 1:
                        self.update({attribute_name: results})
                    else:
                        self.update({attribute_name: results[0]})