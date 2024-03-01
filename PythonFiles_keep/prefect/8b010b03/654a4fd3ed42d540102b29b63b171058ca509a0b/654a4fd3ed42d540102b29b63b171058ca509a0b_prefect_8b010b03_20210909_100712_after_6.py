import uuid
from uuid import uuid4

import pytest
import sqlalchemy as sa

from prefect.orion import models
from prefect.orion.orchestration.rules import OrchestrationResult
from prefect.orion.schemas import responses, states


class TestCreateTaskRun:
    async def test_create_task_run(self, flow_run, client, session):
        task_run_data = {"flow_run_id": str(flow_run.id), "task_key": "my-task-key"}
        response = await client.post("/task_runs/", json=task_run_data)
        assert response.status_code == 201
        assert response.json()["flow_run_id"] == str(flow_run.id)
        assert response.json()["id"]

        task_run = await models.task_runs.read_task_run(
            session=session, task_run_id=response.json()["id"]
        )
        assert task_run.flow_run_id == flow_run.id

    async def test_create_task_run_gracefully_upserts(self, flow_run, client, session):
        # create a task run
        task_run_data = {
            "flow_run_id": str(flow_run.id),
            "task_key": "my-task-key",
            "dynamic_key": "my-dynamic-key",
        }
        task_run_response = await client.post("/task_runs/", json=task_run_data)

        # recreate the same task run, ensure graceful upsert
        response = await client.post("/task_runs/", json=task_run_data)
        assert response.status_code == 200
        assert response.json()["id"] == task_run_response.json()["id"]

    async def test_create_task_run_without_state(self, flow_run, client, session):
        task_run_data = dict(flow_run_id=str(flow_run.id), task_key="task-key")
        response = await client.post("/task_runs/", json=task_run_data)
        task_run = await models.task_runs.read_task_run(
            session=session, task_run_id=response.json()["id"]
        )
        assert str(task_run.id) == response.json()["id"]
        assert task_run.state is None

    async def test_create_task_run_with_state(self, flow_run, client, session):
        task_run_data = dict(
            flow_run_id=str(flow_run.id),
            task_key="task-key",
            state=states.Running().dict(json_compatible=True),
        )
        response = await client.post("/task_runs/", json=task_run_data)
        task_run = await models.task_runs.read_task_run(
            session=session, task_run_id=response.json()["id"]
        )
        assert str(task_run.id) == response.json()["id"]
        assert str(task_run.state.id) == task_run_data["state"]["id"]
        assert task_run.state.type.value == task_run_data["state"]["type"]


class TestReadTaskRun:
    async def test_read_task_run(self, flow_run, task_run, client):
        # make sure we we can read the task run correctly
        response = await client.get(f"/task_runs/{task_run.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(task_run.id)
        assert response.json()["flow_run_id"] == str(flow_run.id)

    async def test_read_flow_run_with_state(self, task_run, client, session):
        state_id = uuid4()
        (
            await models.task_run_states.orchestrate_task_run_state(
                session=session,
                task_run_id=task_run.id,
                state=states.State(id=state_id, type="RUNNING"),
            )
        ).state
        response = await client.get(f"/task_runs/{task_run.id}")
        assert task_run.state.type.value == "RUNNING"
        assert task_run.state.id == state_id

    async def test_read_task_run_returns_404_if_does_not_exist(self, client):
        response = await client.get(f"/task_runs/{uuid4()}")
        assert response.status_code == 404


class TestReadTaskRuns:
    async def test_read_task_runs(self, task_run, client):
        response = await client.get("/task_runs/")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(task_run.id)
        assert response.json()[0]["flow_run_id"] == str(task_run.flow_run_id)

    async def test_read_task_runs_applies_task_run_filter(self, task_run, client):
        response = await client.get(
            "/task_runs/", json={"task_runs": {"ids": [str(task_run.id)]}}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(task_run.id)
        assert response.json()[0]["flow_run_id"] == str(task_run.flow_run_id)

        response = await client.get(
            "/task_runs/", json={"task_runs": {"ids": [str(uuid4())]}}
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_read_task_runs_applies_flow_run_filter(self, task_run, client):
        response = await client.get(
            "/task_runs/", json={"flow_runs": {"ids": [str(task_run.flow_run_id)]}}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(task_run.id)
        assert response.json()[0]["flow_run_id"] == str(task_run.flow_run_id)

        response = await client.get(
            "/task_runs/", json={"flow_runs": {"ids": [str(uuid4())]}}
        )
        assert response.status_code == 200
        assert response.json() == []

    async def test_read_task_runs_applies_flow_filter(self, flow, task_run, client):
        response = await client.get(
            "/task_runs/", json={"flows": {"ids": [str(flow.id)]}}
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(task_run.id)
        assert response.json()[0]["flow_run_id"] == str(task_run.flow_run_id)

        response = await client.get(
            "/task_runs/", json={"flows": {"ids": [str(uuid4())]}}
        )
        assert response.status_code == 200
        assert response.json() == []


class TestDeleteTaskRuns:
    async def test_delete_task_runs(self, task_run, client, session):
        # delete the task run
        response = await client.delete(f"/task_runs/{task_run.id}")
        assert response.status_code == 204

        # make sure it's deleted
        task_run_id = task_run.id
        session.expire_all()
        run = await models.task_runs.read_task_run(
            session=session, task_run_id=task_run_id
        )
        assert run is None
        response = await client.get(f"/task_runs/{task_run_id}")
        assert response.status_code == 404

    async def test_delete_task_run_returns_404_if_does_not_exist(self, client):
        response = await client.delete(f"/task_runs/{uuid4()}")
        assert response.status_code == 404


class TestSetTaskRunState:
    async def test_set_task_run_state(self, task_run, client, session):
        response = await client.post(
            f"/task_runs/{task_run.id}/set_state",
            json=dict(type="RUNNING", name="Test State"),
        )
        assert response.status_code == 201

        api_response = OrchestrationResult.parse_obj(response.json())
        assert api_response.status == responses.SetStateStatus.ACCEPT

        task_run_id = task_run.id
        session.expire_all()
        run = await models.task_runs.read_task_run(
            session=session, task_run_id=task_run_id
        )
        assert run.state.type == states.StateType.RUNNING
        assert run.state.name == "Test State"
        assert run.run_details.run_count == 1

    async def test_failed_becomes_awaiting_retry(self, task_run, client, session):
        # set max retries to 1
        # copy to trigger ORM updates
        task_run.empirical_policy = task_run.empirical_policy.copy()
        task_run.empirical_policy.max_retries = 1
        await session.flush()

        (
            await models.task_run_states.orchestrate_task_run_state(
                session=session,
                task_run_id=task_run.id,
                state=states.Running(),
            )
        ).state
        await session.commit()

        # fail the running task run
        response = await client.post(
            f"/task_runs/{task_run.id}/set_state",
            json=dict(type="FAILED"),
        )
        assert response.status_code == 201

        api_response = OrchestrationResult.parse_obj(response.json())
        assert api_response.status == responses.SetStateStatus.REJECT
        assert api_response.state.name == "Awaiting Retry"
        assert api_response.state.type == states.StateType.SCHEDULED
