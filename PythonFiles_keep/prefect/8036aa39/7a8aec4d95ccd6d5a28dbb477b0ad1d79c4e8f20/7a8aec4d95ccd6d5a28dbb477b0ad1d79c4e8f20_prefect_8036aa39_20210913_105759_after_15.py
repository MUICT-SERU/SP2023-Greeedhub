import os
from pathlib import Path

import pytest
from pydantic import ValidationError

from prefect import flow
from prefect.deployments import (
    DeploymentSpec,
    deployment_specs_from_script,
    deployment_specs_from_yaml,
    load_flow_from_script,
)

from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.flows import Flow
from prefect.exceptions import FlowScriptError, UnspecifiedFlowError, MissingFlowError

from .deployment_test_files.single_flow import hello_world as hello_world_flow

TEST_FILES_DIR = Path(__file__).parent / "deployment_test_files"


class TestDeploymentSpec:
    def test_infers_flow_location_from_flow(self):
        spec = DeploymentSpec(name="test", flow=hello_world_flow)
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")

    def test_flow_location_is_coerced_to_string(self):
        spec = DeploymentSpec(
            name="test", flow_location=TEST_FILES_DIR / "single_flow.py"
        )
        assert type(spec.flow_location) is str
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")

    def test_flow_location_is_absolute(self):
        spec = DeploymentSpec(
            name="test",
            flow_location=(TEST_FILES_DIR / "single_flow.py").relative_to(os.getcwd()),
        )
        assert spec.flow_location == str((TEST_FILES_DIR / "single_flow.py").absolute())

    def test_infers_flow_name_from_flow(self):
        spec = DeploymentSpec(name="test", flow=hello_world_flow)
        assert spec.flow_name == "hello-world"

    def test_checks_for_flow_name_consistency(self):
        with pytest.raises(
            ValidationError, match="`flow.name` and `flow_name` must match"
        ):
            DeploymentSpec(name="test", flow=hello_world_flow, flow_name="other-name")

    def test_loads_flow_and_name_from_location(self):
        spec = DeploymentSpec(
            name="test", flow_location=TEST_FILES_DIR / "single_flow.py"
        )
        assert spec.flow is None
        assert spec.flow_name is None
        spec.load_flow()
        assert isinstance(spec.flow, Flow)
        assert spec.flow.name == "hello-world"
        assert spec.flow_name == "hello-world"

    def test_loads_flow_from_location_by_name(self):
        spec = DeploymentSpec(
            name="test",
            flow_location=TEST_FILES_DIR / "multiple_flows.py",
            flow_name="hello-sun",
        )
        assert spec.flow is None
        assert spec.flow_name == "hello-sun"
        spec.load_flow()
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
            UnspecifiedFlowError, match="Found 2 flows.*'hello-sun' 'hello-moon'"
        ):
            load_flow_from_script(TEST_FILES_DIR / "multiple_flows.py")

    def test_throws_error_when_name_not_found(self):
        with pytest.raises(
            MissingFlowError, match="Flow 'foo' not found.*Found.*'hello-world'"
        ):
            load_flow_from_script(TEST_FILES_DIR / "single_flow.py", flow_name="foo")

    def test_errors_in_flow_script_are_reraised(self):
        with pytest.raises(FlowScriptError) as exc:
            load_flow_from_script(TEST_FILES_DIR / "flow_with_load_error.py")
        script_err = exc.value.__cause__
        assert script_err is not None
        with pytest.raises(RuntimeError, match="This flow shall not load"):
            raise script_err


class TestDeploymentSpecFromFile:
    def test_spec_inline_with_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "inline_deployment.py")
        assert len(specs) == 1
        spec = list(specs)[0]
        assert spec.name == "inline-deployment"
        assert spec.flow.name == "hello-world"
        assert spec.flow_name == "hello-world"
        assert spec.flow_location == str(TEST_FILES_DIR / "inline_deployment.py")

    def test_spec_separate_from_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "single_deployment.py")
        assert len(specs) == 1
        spec = list(specs)[0]
        assert spec.name == "hello-world-daily"
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")
        assert isinstance(spec.schedule, IntervalSchedule)

    def test_multiple_specs_separate_from_flow(self):
        specs = deployment_specs_from_script(TEST_FILES_DIR / "multiple_deployments.py")
        assert len(specs) == 2
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

    def test_spec_from_yaml(self):
        specs = deployment_specs_from_yaml(TEST_FILES_DIR / "single-deployment.yaml")
        assert len(specs) == 1
        spec = list(specs)[0]
        assert spec.name == "hello-world-deployment"
        assert spec.flow_location == str(TEST_FILES_DIR / "single_flow.py")
        assert isinstance(spec.schedule, IntervalSchedule)

    def test_multiple_specs_from_yaml(self):
        specs = deployment_specs_from_yaml(TEST_FILES_DIR / "multiple-deployments.yaml")
        assert len(specs) == 2
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

    def test_loading_spec_does_not_raise_until_flow_is_loaded(self):
        specs = deployment_specs_from_yaml(
            TEST_FILES_DIR / "deployment-with-flow-load-error.yaml"
        )
        assert len(specs) == 1
        spec = list(specs)[0]
        with pytest.raises(FlowScriptError):
            spec.load_flow()
