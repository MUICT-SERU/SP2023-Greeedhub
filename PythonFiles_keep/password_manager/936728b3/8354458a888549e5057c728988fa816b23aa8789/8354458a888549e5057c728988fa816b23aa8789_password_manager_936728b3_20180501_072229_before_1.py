import pytest
from time import sleep
import os
from uuid import uuid4

from password_manager.vault import Vault


def test_create():
    """

    :return:
    0.4126 seconds per test_create
    """
    filename = str(uuid4())
    with Vault('averystrongpassword', path_to_vault=filename):
        pass
    os.remove(filename)


def test_expiry():
    timeout = 5
    filename = str(uuid4())

    with Vault('averystrongpassword', path_to_vault=filename, timeout=timeout) as vault:
        sleep(timeout + 1)
        with pytest.raises(AttributeError):
            print(vault.data)
    os.remove(filename)


def test_save():
    master_password = 'averystrongpassword'
    name = 'reddit'
    password = 'acomplexpassword'
    filename = str(uuid4())

    with Vault(master_password, path_to_vault=filename) as vault:
        vault[name] = {
            'password': password
        }
    with Vault(master_password, path_to_vault=filename) as vault:
        print(vault[name]['password'])
        assert vault[name]['password'] == password
    os.remove(filename)


def test_bad_save():
    master_password = 'averystrongpassword'
    name = 'reddit'
    filename = str(uuid4())

    with pytest.raises(ValueError):
        with Vault(master_password, path_to_vault=filename) as vault:
            vault[name] = dict()
    os.remove(filename)


if __name__ == '__main__':
    from MyUtils.testing.repeat import timeit
    # test_expiry()
    # timeit(test_create)
    test_save()
