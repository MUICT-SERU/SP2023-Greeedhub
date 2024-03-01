import os
import textwrap
from datetime import timedelta
from pathlib import Path
from unittest.mock import MagicMock

import pytest
from pydantic import ValidationError

from prefect.blocks.storage import FileStorageBlock
from prefect.deployments import (
    DeploymentSpec,
    deployment_specs_from_script,
    deployment_specs_from_yaml,
    load_flow_from_deployment,
    load_flow_from_script,
)
from prefect.exceptions import (
    MissingFlowError,
    ScriptError,
    SpecValidationError,
    UnspecifiedFlowError,
)
from prefect.flow_runners import SubprocessFlowRunner
from prefect.flows import Flow, flow
from prefect.orion.schemas.core import Deployment
from prefect.orion.schemas.data import DataDocument
from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.orion.serializers import D

from .deployment_test_files.single_flow import hello_world as hello_world_flow

TEST_FILES_DIR = Path(__file__).parent / "deployment_test_files"


@pytest.fixture
async def tmp_file_storage_block(tmp_path, orion_client, session):
    # Workaround until `read_block_spec_by_name_and_version` is exposed on client
    from prefect.orion.models.block_specs import read_block_spec_by_name_and_version

    block = FileStorageBlock(base_path=str(tmp_path))
    block_spec = await read_block_spec_by_name_and_version(
        session, block._block_spec_name, block._block_spec_version
    )
    block_id = await orion_client.create_block(
        block, block_spec_id=block_spec.id, name="test"
    )
    return block_id


class TestDeploymentSpec:
    @pytest.fixture(autouse=True)
    async def default_storage(self, orion_client, tmp_file_storage_block):
        # A "remote" default storage is required for the default flow runner type
        await orion_client.set_default_storage_block(tmp_file_storage_block)

    async def test_infers_flow_location_from_flow(self):
        spec = DeploymentSpec(flow=hello_world_flow)
        await spec.validate()
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")

    async def test_flow_location_is_coerced_to_string(self):
        spec = DeploymentSpec(flow_location=TEST_FILES_DIR / "single_flow.py")
        await spec.validate()
        assert type(spec.flow_location) is str
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")

    def test_flow_location_is_absolute(self):
        spec = DeploymentSpec(
            flow_location=(TEST_FILES_DIR / "single_flow.py").relative_to(os.getcwd()),
        )
        assert spec.flow_location == str((TEST_FILES_DIR / "single_flow.py").absolute())

    async def test_infers_flow_name_from_flow(self):
        spec = DeploymentSpec(flow=hello_world_flow)
        await spec.validate()
        assert spec.flow_name == "hello-world"

    async def test_checks_for_flow_name_consistency(self):
        spec = DeploymentSpec(flow=hello_world_flow, flow_name="other-name")
        with pytest.raises(
            SpecValidationError, match="`flow.name` and `flow_name` must match"
        ):
            await spec.validate()

    async def test_loads_flow_and_name_from_location(self):
        spec = DeploymentSpec(
            name="test", flow_location=TEST_FILES_DIR / "single_flow.py"
        )
        assert spec.flow is None
        assert spec.flow_name is None
        await spec.validate()
        assert isinstance(spec.flow, Flow)
        assert spec.flow.name == "hello-world"
        assert spec.flow_name == "hello-world"

    async def test_loads_flow_from_location_by_name(self):
        spec = DeploymentSpec(
            name="test",
            flow_location=TEST_FILES_DIR / "multiple_flows.py",
            flow_name="hello-sun",
        )
        assert spec.flow is None
        assert spec.flow_name == "hello-sun"
        await spec.validate()
        assert isinstance(spec.flow, Flow)
        assert spec.flow.name == "hello-sun"
        assert spec.flow_name == "hello-sun"


class TestLoadFlowFromScript:
    def test_loads_from_file_with_one_flow(self):
        loaded_flow = load_flow_from_script(TEST_FILES_DIR / "single_flow.py")
        assert isinstance(loaded_flow, Flow)
        assert loaded_flow.name == "hello-world"

    def test_loads_from_file_with_multiple_flows_by_name(self):
        loaded_flow = load_flow_from_script(
            TEST_FILES_DIR / "multiple_flows.py", flow_name="hello-moon"
        )
        assert isinstance(loaded_flow, Flow)
        assert loaded_flow.name == "hello-moon"
        loaded_flow = load_flow_from_script(
            TEST_FILES_DIR / "multiple_flows.py", flow_name="hello-sun"
        )
        assert isinstance(loaded_flow, Flow)
        assert loaded_flow.name == "hello-sun"

    def test_requires_name_for_file_with_multiple_flows(self):
        with pytest.raises(
            UnspecifiedFlowError, match="Found 2 flows.*'hello-moon' 'hello-sun'"
        ):
            load_flow_from_script(TEST_FILES_DIR / "multiple_flows.py")

    def test_throws_error_when_name_not_found(self):
        with pytest.raises(
            MissingFlowError, match="Flow 'foo' not found.*Found.*'hello-world'"
        ):
            load_flow_from_script(TEST_FILES_DIR / "single_flow.py", flow_name="foo")

    def test_errors_in_flow_script_are_reraised(self):
        with pytest.raises(ScriptError) as exc:
            load_flow_from_script(TEST_FILES_DIR / "flow_with_load_error.py")
        script_err = exc.value.__cause__
        assert script_err is not None
        with pytest.raises(RuntimeError, match="This flow shall not load"):
            raise script_err


class TestDeploymentSpecFromFile:
    @pytest.fixture(autouse=True)
    async def default_storage(self, orion_client, tmp_file_storage_block):
        # A "remote" default storage is required for the default flow runner type
        await orion_client.set_default_storage_block(tmp_file_storage_block)

    async def test_spec_inline_with_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "inline_deployment.py")
        assert len(specs) == 1
        spec = list(specs)[0]
        await spec.validate()
        assert spec.name == "inline-deployment"
        assert spec.flow.name == "hello-world"
        assert spec.flow_name == "hello-world"
        assert spec.flow_location == str(TEST_FILES_DIR / "inline_deployment.py")
        assert spec.parameters == {"name": "Marvin"}
        assert spec.tags == ["foo", "bar"]

    async def test_spec_separate_from_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "single_deployment.py")
        assert len(specs) == 1
        spec = list(specs)[0]
        await spec.validate()
        assert spec.name == "hello-world-daily"
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")
        assert isinstance(spec.schedule, IntervalSchedule)
        assert spec.parameters == {"foo": "bar"}
        assert spec.tags == ["foo", "bar"]

    async def test_multiple_specs_separate_from_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "multiple_deployments.py")
        assert len(specs) == 2
        for spec in specs:
            await spec.validate()
        specs_by_name = {spec.name: spec for spec in specs}
        assert set(specs_by_name.keys()) == {
            "hello-sun-deployment",
            "hello-moon-deployment",
        }
        sun_deploy = specs_by_name["hello-sun-deployment"]
        moon_deploy = specs_by_name["hello-moon-deployment"]
        assert sun_deploy.flow_location == str(TEST_FILES_DIR / "multiple_flows.py")
        assert sun_deploy.flow_name == "hello-sun"
        assert moon_deploy.flow_location == str(TEST_FILES_DIR / "multiple_flows.py")
        assert moon_deploy.flow_name == "hello-moon"

    async def test_spec_from_yaml(self):
        specs = deployment_specs_from_yaml(TEST_FILES_DIR / "single-deployment.yaml")
        assert len(specs) == 1
        spec = list(specs)[0]
        await spec.validate()
        assert spec.name == "hello-world-deployment"
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")
        assert isinstance(spec.schedule, IntervalSchedule)
        assert spec.parameters == {"foo": "bar"}
        assert spec.tags == ["foo", "bar"]

    async def test_multiple_specs_from_yaml(self):
        specs = deployment_specs_from_yaml(TEST_FILES_DIR / "multiple-deployments.yaml")
        assert len(specs) == 2
        for spec in specs:
            await spec.validate()
        specs_by_name = {spec.name: spec for spec in specs}
        assert set(specs_by_name.keys()) == {
            "hello-sun-deployment",
            "hello-moon-deployment",
        }
        sun_deploy = specs_by_name["hello-sun-deployment"]
        moon_deploy = specs_by_name["hello-moon-deployment"]
        assert sun_deploy.flow_location == str(TEST_FILES_DIR / "multiple_flows.py")
        assert sun_deploy.flow_name == "hello-sun"
        assert moon_deploy.flow_location == str(TEST_FILES_DIR / "multiple_flows.py")
        assert moon_deploy.flow_name == "hello-moon"

    async def test_loading_spec_does_not_raise_until_flow_is_loaded(self):
        specs = deployment_specs_from_yaml(
            TEST_FILES_DIR / "deployment-with-flow-load-error.yaml"
        )
        assert len(specs) == 1
        spec = list(specs)[0]
        with pytest.raises(ScriptError):
            await spec.validate()

    async def test_create_deployment(self, orion_client):
        schedule = IntervalSchedule(interval=timedelta(days=1))

        spec = DeploymentSpec(
            name="test",
            flow_location=TEST_FILES_DIR / "single_flow.py",
            schedule=schedule,
            parameters={"foo": "bar"},
            tags=["foo", "bar"],
            flow_runner=SubprocessFlowRunner(env={"FOO": "BAR"}),
        )
        deployment_id = await spec.create_deployment(client=orion_client)

        # Deployment was created in backend
        lookup = await orion_client.read_deployment(deployment_id)
        assert lookup.name == "test"
        assert lookup.schedule == schedule
        assert lookup.parameters == {"foo": "bar"}
        assert lookup.tags == ["foo", "bar"]
        assert lookup.flow_runner == spec.flow_runner.to_settings()

        # Flow was loaded
        assert spec.flow is not None


class TestLoadFlowFromDeployment:
    @pytest.fixture
    def flow_object(self):
        @flow
        def foo():
            pass

        return foo

    @pytest.fixture
    async def flow_id(self, flow_object, orion_client):
        return await orion_client.create_flow(flow_object)

    async def test_load_pickled_flow_from_deployment(
        self, flow_object, flow_id, orion_client
    ):
        deployment = Deployment(
            name="test",
            flow_id=flow_id,
            flow_data=DataDocument.encode("cloudpickle", flow_object),
        )
        loaded_flow_object = await load_flow_from_deployment(
            deployment, client=orion_client
        )
        assert flow_object == loaded_flow_object

    async def test_load_persisted_flow_pickle_from_deployment(
        self, flow_object, flow_id, orion_client
    ):
        deployment = Deployment(
            name="test",
            flow_id=flow_id,
            flow_data=await orion_client.persist_object(flow_object),
        )
        loaded_flow_object = await load_flow_from_deployment(
            deployment, client=orion_client
        )
        assert isinstance(loaded_flow_object, Flow)
        assert flow_object.name == loaded_flow_object.name

    async def test_load_persisted_flow_script_from_deployment(
        self, flow_object, flow_id, orion_client
    ):
        deployment = Deployment(
            name="test",
            flow_id=flow_id,
            flow_data=await orion_client.persist_object(
                textwrap.dedent(
                    """
                    from prefect import flow

                    @flow
                    def foo():
                        pass
                    """
                ),
                encoder="text",
            ),
        )
        loaded_flow_object = await load_flow_from_deployment(
            deployment, client=orion_client
        )
        assert isinstance(loaded_flow_object, Flow)
        assert flow_object.name == loaded_flow_object.name

    async def test_load_bad_flow_script_from_deployment(self, flow_id, orion_client):
        deployment = Deployment(
            name="test",
            flow_id=flow_id,
            flow_data=await orion_client.persist_object(
                "test",
                encoder="text",
            ),
        )
        with pytest.raises(ScriptError):
            await load_flow_from_deployment(deployment, client=orion_client)
