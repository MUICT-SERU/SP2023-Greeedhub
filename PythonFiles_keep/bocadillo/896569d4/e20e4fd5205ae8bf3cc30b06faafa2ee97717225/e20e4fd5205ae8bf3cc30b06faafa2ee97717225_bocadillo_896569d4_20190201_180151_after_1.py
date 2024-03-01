import asyncio
import json
from typing import NamedTuple

import pytest
from click.testing import CliRunner

from bocadillo import API


# FIX: the default fixture from `pytest-asyncio` closes the event loop,
# which for some reason causes tests that use a live server to fail.
# (Perhaps because they'll try to close the loop themselves and fail).
# For the default fixture, see:
# https://github.com/pytest-dev/pytest-asyncio/blob/master/pytest_asyncio/plugin.py#L204
@pytest.fixture
def event_loop():
    return asyncio.get_event_loop_policy().new_event_loop()


@pytest.fixture
def api():
    _api = API()
    _websocket_connect = _api.client.websocket_connect

    def websocket_connect(url, *args, **kwargs):
        session = _websocket_connect(url, *args, **kwargs)
        # Receives bytes by default
        session.receive_json = lambda: json.loads(session.receive_text())
        # Sends bytes by default
        session.send_json = lambda value: session.send_text(json.dumps(value))
        return session

    _api.client.websocket_connect = websocket_connect
    return _api


class TemplateWrapper(NamedTuple):
    name: str
    context: dict
    rendered: str
    source_directory: str


def _create_template(api, tmpdir_factory, dirname):
    templates_dir = tmpdir_factory.mktemp(dirname)
    template_file = templates_dir.join("hello.html")
    template_file.write("<h1>Hello, {{ name }}!</h1>")
    api.templates_dir = str(templates_dir)
    return TemplateWrapper(
        name="hello.html",
        context={"name": "Bocadillo"},
        rendered="<h1>Hello, Bocadillo!</h1>",
        source_directory=dirname,
    )


@pytest.fixture
def template_file(api: API, tmpdir_factory):
    return _create_template(api, tmpdir_factory, dirname="templates")


@pytest.fixture
def template_file_elsewhere(api: API, tmpdir_factory):
    return _create_template(api, tmpdir_factory, dirname="templates_elsewhere")


@pytest.fixture
def runner():
    return CliRunner()
