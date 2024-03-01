from uuid import uuid4

import pytest
import sqlalchemy as sa

from prefect.orion import models, schemas
from prefect.orion.orchestration.rules import OrchestrationResult
from prefect.orion.schemas import actions, core, responses, states


class TestCreateFlowRun:
    async def test_create_flow_run(self, flow, client, session):
        flow_run_data = {"flow_id": str(flow.id)}
        response = await client.post("/flow_runs/", json=flow_run_data)
        assert response.status_code == 201
        assert response.json()["flow_id"] == str(flow.id)
        assert response.json()["id"]

        flow_run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=response.json()["id"]
        )
        assert flow_run.flow_id == flow.id

    async def test_create_multiple_flow_runs(self, flow, client, session):
        response1 = await client.post("/flow_runs/", json={"flow_id": str(flow.id)})
        response2 = await client.post("/flow_runs/", json={"flow_id": str(flow.id)})
        assert response1.status_code == 201
        assert response2.status_code == 201
        assert response1.json()["flow_id"] == str(flow.id)
        assert response2.json()["flow_id"] == str(flow.id)
        assert response1.json()["id"] != response2.json()["id"]

        result = await session.execute(
            sa.select(models.orm.FlowRun.id).filter_by(flow_id=flow.id)
        )
        ids = result.scalars().all()
        assert {response1.json()["id"], response2.json()["id"]} == {str(i) for i in ids}

    async def test_create_flow_run_with_idempotency_key_recovers_original_flow_run(
        self, flow, client, session
    ):
        flow_run_data = {"flow_id": str(flow.id), "idempotency_key": "test-key"}
        response1 = await client.post("/flow_runs/", json=flow_run_data)
        assert response1.status_code == 201

        response2 = await client.post("/flow_runs/", json=flow_run_data)
        assert response2.status_code == 200
        assert response1.json()["id"] == response2.json()["id"]

    async def test_create_flow_run_with_idempotency_key_across_multiple_flows(
        self, flow, client, session
    ):
        flow2 = models.orm.Flow(name="another flow")
        session.add(flow2)
        await session.commit()

        response1 = await client.post(
            "/flow_runs/", json={"flow_id": str(flow.id), "idempotency_key": "test-key"}
        )
        assert response1.status_code == 201

        response2 = await client.post(
            "/flow_runs/",
            json={"flow_id": str(flow2.id), "idempotency_key": "test-key"},
        )
        assert response2.status_code == 201
        assert response1.json()["id"] != response2.json()["id"]

    async def test_create_flow_run_with_subflow_information(
        self, flow, task_run, client, session
    ):
        flow_run_data = dict(
            flow_id=str(flow.id),
            parent_task_run_id=str(task_run.id),
        )
        response = await client.post("/flow_runs/", json=flow_run_data)

        flow_run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=response.json()["id"]
        )
        assert flow_run.parent_task_run_id == task_run.id

    async def test_create_flow_run_without_state(self, flow, client, session):
        flow_run_data = dict(
            flow_id=str(flow.id),
        )
        response = await client.post("/flow_runs/", json=flow_run_data)
        flow_run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=response.json()["id"]
        )
        assert str(flow_run.id) == response.json()["id"]
        assert flow_run.state is None

    async def test_create_flow_run_with_state(self, flow, client, session):
        flow_run_data = dict(
            flow_id=str(flow.id),
            state=states.Running().dict(json_compatible=True),
        )
        response = await client.post("/flow_runs/", json=flow_run_data)
        flow_run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=response.json()["id"]
        )
        assert str(flow_run.id) == response.json()["id"]
        assert str(flow_run.state.id) == flow_run_data["state"]["id"]
        assert flow_run.state.type.value == flow_run_data["state"]["type"]

    async def test_create_flow_run_with_deployment_id(self, flow, client, session):

        deployment = await models.deployments.create_deployment(
            session=session,
            deployment=core.Deployment(name="", flow_id=flow.id),
        )
        await session.commit()

        response = await client.post(
            "/flow_runs/",
            json=actions.FlowRunCreate(
                flow_id=flow.id, deployment_id=deployment.id
            ).dict(json_compatible=True),
        )

        assert response.json()["deployment_id"] == str(deployment.id)


class TestReadFlowRun:
    async def test_read_flow_run(self, flow, flow_run, client):
        # make sure we we can read the flow run correctly
        response = await client.get(f"/flow_runs/{flow_run.id}")
        assert response.status_code == 200
        assert response.json()["id"] == str(flow_run.id)
        assert response.json()["flow_id"] == str(flow.id)

    async def test_read_flow_run_with_state(self, flow_run, client, session):
        state_id = uuid4()
        (
            await models.flow_run_states.orchestrate_flow_run_state(
                session=session,
                flow_run_id=flow_run.id,
                state=states.State(id=state_id, type="RUNNING"),
            )
        ).state
        response = await client.get(f"/flow_runs/{flow_run.id}")
        assert flow_run.state.type.value == "RUNNING"
        assert flow_run.state.id == state_id

    async def test_read_flow_run_returns_404_if_does_not_exist(self, client):
        response = await client.get(f"/flow_runs/{uuid4()}")
        assert response.status_code == 404


class TestReadFlowRuns:
    @pytest.fixture
    async def flow_runs(self, flow, session):
        flow_2 = await models.flows.create_flow(
            session=session,
            flow=actions.FlowCreate(name="another-test"),
        )

        flow_run_1 = await models.flow_runs.create_flow_run(
            session=session,
            flow_run=actions.FlowRunCreate(flow_id=flow.id),
        )
        flow_run_2 = await models.flow_runs.create_flow_run(
            session=session,
            flow_run=actions.FlowRunCreate(flow_id=flow.id),
        )
        flow_run_3 = await models.flow_runs.create_flow_run(
            session=session,
            flow_run=actions.FlowRunCreate(flow_id=flow_2.id),
        )
        await session.commit()
        return [flow_run_1, flow_run_2, flow_run_3]

    async def test_read_flow_runs(self, flow_runs, client):
        response = await client.get("/flow_runs/")
        assert response.status_code == 200
        assert len(response.json()) == 3

    async def test_read_flow_runs_applies_flow_filter(self, flow, flow_runs, client):
        response = await client.get(
            "/flow_runs/", json=dict(flows=dict(ids=[str(flow.id)]))
        )
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_read_flow_runs_applies_flow_run_filter(
        self, flow, flow_runs, client
    ):
        response = await client.get(
            "/flow_runs/", json=dict(flow_runs=dict(ids=[str(flow_runs[0].id)]))
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(flow_runs[0].id)

    async def test_read_flow_runs_applies_task_run_filter(
        self, flow, flow_runs, client, session
    ):
        task_run_1 = await models.task_runs.create_task_run(
            session=session,
            task_run=schemas.actions.TaskRunCreate(
                flow_run_id=flow_runs[1].id, task_key="my-key"
            ),
        )
        await session.commit()
        response = await client.get(
            "/flow_runs/", json=dict(task_runs=dict(ids=[str(task_run_1.id)]))
        )
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["id"] == str(flow_runs[1].id)

    async def test_read_flow_runs_applies_limit(self, flow_runs, client):
        response = await client.get("/flow_runs/", json=dict(pagination=dict(limit=1)))
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_read_flow_runs_returns_empty_list(self, client):
        response = await client.get("/flow_runs/")
        assert response.status_code == 200
        assert response.json() == []


class TestDeleteFlowRuns:
    async def test_delete_flow_runs(self, flow_run, client, session):
        # delete the flow run
        response = await client.delete(f"/flow_runs/{flow_run.id}")
        assert response.status_code == 204

        # make sure it's deleted (first grab its ID)
        flow_run_id = flow_run.id
        session.expire_all()

        run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=flow_run_id
        )
        assert run is None
        response = await client.get(f"/flow_runs/{flow_run_id}")
        assert response.status_code == 404

    async def test_delete_flow_run_returns_404_if_does_not_exist(self, client):
        response = await client.delete(f"/flow_runs/{uuid4()}")
        assert response.status_code == 404


class TestSetFlowRunState:
    async def test_set_flow_run_state(self, flow_run, client, session):
        response = await client.post(
            f"/flow_runs/{flow_run.id}/set_state",
            json=dict(type="RUNNING", name="Test State"),
        )
        assert response.status_code == 201

        api_response = OrchestrationResult.parse_obj(response.json())
        assert api_response.status == responses.SetStateStatus.ACCEPT

        flow_run_id = flow_run.id
        session.expire(flow_run)

        run = await models.flow_runs.read_flow_run(
            session=session, flow_run_id=flow_run_id
        )
        assert run.state.type == states.StateType.RUNNING
        assert run.state.name == "Test State"
