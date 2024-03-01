from dataclasses import dataclass
from datetime import timedelta
from uuid import UUID

import pendulum
import pytest
from pydantic import BaseModel

from prefect import flow
from prefect.client import OrionClient
from prefect.orion import schemas
from prefect.orion.orchestration.rules import OrchestrationResult
from prefect.orion.schemas.data import DataDocument
from prefect.orion.schemas.states import Scheduled, Pending, Running, StateType
from prefect.tasks import task
from prefect.orion.schemas.schedules import IntervalSchedule
from prefect.flow_runners import UniversalFlowRunner


async def test_hello(orion_client):
    response = await orion_client.hello()
    assert response.json() == "👋"


async def test_create_then_read_flow(orion_client):
    @flow
    def foo():
        pass

    flow_id = await orion_client.create_flow(foo)
    assert isinstance(flow_id, UUID)

    lookup = await orion_client.read_flow(flow_id)
    assert isinstance(lookup, schemas.core.Flow)
    assert lookup.name == foo.name


async def test_create_then_read_deployment(orion_client):
    @flow
    def foo():
        pass

    flow_id = await orion_client.create_flow(foo)
    schedule = IntervalSchedule(interval=timedelta(days=1))
    flow_data = DataDocument.encode("cloudpickle", foo)

    deployment_id = await orion_client.create_deployment(
        flow_id=flow_id,
        name="test-deployment",
        flow_data=flow_data,
        schedule=schedule,
        parameters={"foo": "bar"},
        tags=["foo", "bar"],
        flow_runner=UniversalFlowRunner(env={"foo": "bar"}),
    )

    lookup = await orion_client.read_deployment(deployment_id)
    assert isinstance(lookup, schemas.core.Deployment)
    assert lookup.name == "test-deployment"
    assert lookup.flow_data == flow_data
    assert lookup.schedule == schedule
    assert lookup.parameters == {"foo": "bar"}
    assert lookup.tags == ["foo", "bar"]
    assert lookup.flow_runner == UniversalFlowRunner(env={"foo": "bar"}).to_settings()


async def test_read_deployment_by_name(orion_client):
    @flow
    def foo():
        pass

    flow_id = await orion_client.create_flow(foo)
    schedule = IntervalSchedule(interval=timedelta(days=1))
    flow_data = DataDocument.encode("cloudpickle", foo)

    deployment_id = await orion_client.create_deployment(
        flow_id=flow_id,
        name="test-deployment",
        flow_data=flow_data,
        schedule=schedule,
    )

    lookup = await orion_client.read_deployment_by_name("foo/test-deployment")
    assert isinstance(lookup, schemas.core.Deployment)
    assert lookup.id == deployment_id
    assert lookup.name == "test-deployment"
    assert lookup.flow_data == flow_data
    assert lookup.schedule == schedule


async def test_create_then_read_flow_run(orion_client):
    @flow
    def foo():
        pass

    flow_run = await orion_client.create_flow_run(
        foo, name="zachs-flow-run", flow_runner=UniversalFlowRunner(env={"foo": "bar"})
    )
    assert isinstance(flow_run, schemas.core.FlowRun)

    lookup = await orion_client.read_flow_run(flow_run.id)
    # Estimates will not be equal since time has passed
    lookup.estimated_start_time_delta = flow_run.estimated_start_time_delta
    lookup.estimated_run_time = flow_run.estimated_run_time
    assert lookup == flow_run


async def test_create_flow_run_retains_parameters(orion_client):
    @flow
    def foo():
        pass

    parameters = {"x": 1, "y": [1, 2, 3]}

    flow_run = await orion_client.create_flow_run(
        foo, name="zachs-flow-run", parameters=parameters
    )
    assert parameters == flow_run.parameters, "Parameter contents are equal"
    assert id(flow_run.parameters) == id(parameters), "Original objects retained"


async def test_create_flow_run_with_state(orion_client):
    @flow
    def foo():
        pass

    flow_run = await orion_client.create_flow_run(foo, state=schemas.states.Running())
    assert flow_run.state.is_running()


async def test_set_then_read_flow_run_state(orion_client):
    @flow
    def foo():
        pass

    flow_run_id = (await orion_client.create_flow_run(foo)).id
    response = await orion_client.set_flow_run_state(
        flow_run_id,
        state=schemas.states.Completed(message="Test!"),
    )
    assert isinstance(response, OrchestrationResult)
    assert response.status == schemas.responses.SetStateStatus.ACCEPT

    states = await orion_client.read_flow_run_states(flow_run_id)
    assert len(states) == 2

    assert states[0].is_pending()

    assert states[1].is_completed()
    assert states[1].message == "Test!"


async def test_read_flow_runs_without_filter(orion_client):
    @flow
    def foo():
        pass

    fr_id_1 = (await orion_client.create_flow_run(foo)).id
    fr_id_2 = (await orion_client.create_flow_run(foo)).id

    flow_runs = await orion_client.read_flow_runs()
    assert len(flow_runs) == 2
    assert all(isinstance(flow_run, schemas.core.FlowRun) for flow_run in flow_runs)
    assert {flow_run.id for flow_run in flow_runs} == {fr_id_1, fr_id_2}


async def test_read_flow_runs_with_filtering(orion_client):
    @flow
    def foo():
        pass

    @flow
    def bar():
        pass

    fr_id_1 = (await orion_client.create_flow_run(foo, state=Pending())).id
    fr_id_2 = (await orion_client.create_flow_run(foo, state=Scheduled())).id
    fr_id_3 = (await orion_client.create_flow_run(bar, state=Pending())).id
    # Only below should match the filter
    fr_id_4 = (await orion_client.create_flow_run(bar, state=Scheduled())).id
    fr_id_5 = (await orion_client.create_flow_run(bar, state=Running())).id

    flow_runs = await orion_client.read_flow_runs(
        flow_filter=schemas.filters.FlowFilter(name=dict(any_=["bar"])),
        flow_run_filter=schemas.filters.FlowRunFilter(
            state=dict(
                type=dict(
                    any_=[
                        StateType.SCHEDULED,
                        StateType.RUNNING,
                    ]
                )
            )
        ),
    )
    assert len(flow_runs) == 2
    assert all(isinstance(flow, schemas.core.FlowRun) for flow in flow_runs)
    assert {flow_run.id for flow_run in flow_runs} == {fr_id_4, fr_id_5}


async def test_read_flows_without_filter(orion_client):
    @flow
    def foo():
        pass

    @flow
    def bar():
        pass

    flow_id_1 = await orion_client.create_flow(foo)
    flow_id_2 = await orion_client.create_flow(bar)

    flows = await orion_client.read_flows()
    assert len(flows) == 2
    assert all(isinstance(flow, schemas.core.Flow) for flow in flows)
    assert {flow.id for flow in flows} == {flow_id_1, flow_id_2}


async def test_read_flows_with_filter(orion_client):
    @flow
    def foo():
        pass

    @flow
    def bar():
        pass

    @flow
    def foobar():
        pass

    flow_id_1 = await orion_client.create_flow(foo)
    flow_id_2 = await orion_client.create_flow(bar)
    flow_id_3 = await orion_client.create_flow(foobar)

    flows = await orion_client.read_flows(
        flow_filter=schemas.filters.FlowFilter(name=dict(any_=["foo", "bar"]))
    )
    assert len(flows) == 2
    assert all(isinstance(flow, schemas.core.Flow) for flow in flows)
    assert {flow.id for flow in flows} == {flow_id_1, flow_id_2}


async def test_create_flow_run_from_deployment(orion_client, deployment):
    flow_run = await orion_client.create_flow_run_from_deployment(deployment.id)
    # Deployment details attached
    assert flow_run.deployment_id == deployment.id
    assert flow_run.flow_id == deployment.flow_id
    # Includes flow runner
    assert flow_run.flow_runner.dict() == deployment.flow_runner.dict()
    # Flow version is not populated yet
    assert flow_run.flow_version is None
    # State is scheduled for now
    assert flow_run.state.type == schemas.states.StateType.SCHEDULED
    assert (
        pendulum.now("utc")
        .diff(flow_run.state.state_details.scheduled_time)
        .in_seconds()
        < 1
    )


async def test_update_flow_run(orion_client):
    @flow
    def foo():
        pass

    flow_run = await orion_client.create_flow_run(foo)

    exclude = {"updated", "lateness_estimate", "estimated_start_time_delta"}

    # No mutation for unset fields
    await orion_client.update_flow_run(flow_run.id)
    unchanged_flow_run = await orion_client.read_flow_run(flow_run.id)
    assert unchanged_flow_run.dict(exclude=exclude) == flow_run.dict(exclude=exclude)

    # Fields updated when set
    await orion_client.update_flow_run(
        flow_run.id, flow_version="foo", parameters={"foo": "bar"}, name="test"
    )
    updated_flow_run = await orion_client.read_flow_run(flow_run.id)
    assert updated_flow_run.flow_version == "foo"
    assert updated_flow_run.parameters == {"foo": "bar"}
    assert updated_flow_run.name == "test"


async def test_create_then_read_task_run(orion_client):
    @flow
    def foo():
        pass

    @task(tags=["a", "b"], retries=3)
    def bar(orion_client):
        pass

    flow_run = await orion_client.create_flow_run(foo)
    task_run = await orion_client.create_task_run(
        bar, flow_run_id=flow_run.id, dynamic_key="0"
    )
    assert isinstance(task_run, schemas.core.TaskRun)

    lookup = await orion_client.read_task_run(task_run.id)
    # Estimates will not be equal since time has passed
    lookup.estimated_start_time_delta = task_run.estimated_start_time_delta
    lookup.estimated_run_time = task_run.estimated_run_time
    assert lookup == task_run


async def test_create_then_read_task_run_with_state(orion_client):
    @flow
    def foo():
        pass

    @task(tags=["a", "b"], retries=3)
    def bar(orion_client):
        pass

    flow_run = await orion_client.create_flow_run(foo)
    task_run = await orion_client.create_task_run(
        bar, flow_run_id=flow_run.id, state=schemas.states.Running(), dynamic_key="0"
    )
    assert task_run.state.is_running()


async def test_set_then_read_task_run_state(orion_client):
    @flow
    def foo():
        pass

    @task
    def bar(orion_client):
        pass

    flow_run = await orion_client.create_flow_run(foo)
    task_run = await orion_client.create_task_run(
        bar, flow_run_id=flow_run.id, dynamic_key="0"
    )

    response = await orion_client.set_task_run_state(
        task_run.id,
        schemas.states.Completed(message="Test!"),
    )

    assert isinstance(response, OrchestrationResult)
    assert response.status == schemas.responses.SetStateStatus.ACCEPT

    run = await orion_client.read_task_run(task_run.id)
    assert isinstance(run.state, schemas.states.State)
    assert run.state.type == schemas.states.StateType.COMPLETED
    assert run.state.message == "Test!"


@dataclass
class ExDataClass:
    x: int


class ExPydanticModel(BaseModel):
    x: int


@pytest.mark.parametrize(
    "put_obj",
    [
        "hello",
        7,
        ExDataClass(x=1),
        ExPydanticModel(x=0),
    ],
)
async def test_put_then_retrieve_object(put_obj, orion_client):
    datadoc = await orion_client.persist_object(put_obj)
    assert datadoc.encoding == "orion"
    retrieved_obj = await orion_client.retrieve_object(datadoc)
    assert retrieved_obj == put_obj


async def test_client_non_async_with_is_helpful():
    with pytest.raises(RuntimeError, match="must be entered with an async context"):
        with OrionClient():
            pass


class TestResolveDataDoc:
    async def test_does_not_allow_other_types(self, orion_client):
        with pytest.raises(TypeError, match="invalid type str"):
            await orion_client.resolve_datadoc("foo")

    async def test_resolves_data_document(self, orion_client):
        assert (
            await orion_client.resolve_datadoc(
                DataDocument.encode("cloudpickle", "hello")
            )
            == "hello"
        )

    async def test_resolves_nested_data_documents(self, orion_client):
        assert (
            await orion_client.resolve_datadoc(
                DataDocument.encode("cloudpickle", DataDocument.encode("json", "hello"))
            )
            == "hello"
        )

    async def test_resolves_nested_data_documents_when_inner_is_bytes(
        self, orion_client
    ):
        assert (
            await orion_client.resolve_datadoc(
                DataDocument.encode(
                    "cloudpickle", DataDocument.encode("json", "hello").json().encode()
                )
            )
            == "hello"
        )

    async def test_resolves_persisted_data_documents(self, orion_client):
        async with OrionClient() as client:
            assert (
                await orion_client.resolve_datadoc(
                    await client.persist_data(
                        DataDocument.encode("json", "hello").json().encode()
                    ),
                )
                == "hello"
            )
