import pytest
from os import getcwd, path, remove
from sentry_config.exceptions import *

ini_path = getcwd() + "/test_ini.ini"


def remove_existing_ini():
    if path.exists(ini_path):
        remove(ini_path)


@pytest.fixture()
def config(request):
    from configs import TestConfig

    request.addfinalizer(remove_existing_ini)
    config_container = TestConfig(ini_path)
    config_container.flush_config()

    return config_container


@pytest.fixture()
def erroneous_config(request):
    from configs import TestConfigErroneous

    request.addfinalizer(remove_existing_ini)
    config_container = TestConfigErroneous(ini_path)
    config_container.flush_config()

    return config_container


class TestConfig:
    def test_read(self, config):
        config.read_config()
        assert config.TestSection.IntOption == 5
        assert config.TestSection.BoolOption is True


class TestConfigErroneous:
    def test_read(self, erroneous_config):
        with pytest.raises((CriteriaNotMetError, NoDefaultGivenError)) as excinfo:
            erroneous_config.read_config()

        assert "Criteria not met" or "does not have a default value" in str(excinfo.value)
