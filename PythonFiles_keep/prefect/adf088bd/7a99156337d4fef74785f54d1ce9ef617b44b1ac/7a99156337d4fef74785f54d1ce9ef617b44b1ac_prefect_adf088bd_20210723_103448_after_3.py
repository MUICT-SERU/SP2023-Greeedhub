import pytest
import pendulum
from uuid import uuid4
from prefect.orion import models, schemas


class TestCreateFlowRunState:
    async def test_create_flow_run_state(self, flow_run, client, database_session):
        flow_run_state_data = {
            "flow_run_id": flow_run.id,
            "state": schemas.actions.StateCreate(type="RUNNING").json_dict(),
        }
        response = await client.post("/flow_run_states/", json=flow_run_state_data)
        assert response.status_code == 200
        assert response.json()["id"]

        flow_run_state = await models.flow_run_states.read_flow_run_state(
            session=database_session, flow_run_state_id=response.json()["id"]
        )
        assert flow_run_state.flow_run_id == flow_run.id

    async def test_create_flow_run_state_requires_flow_run_id(
        self, flow_run, client, database_session
    ):
        flow_run_state_data = {
            "flow_run_id": None,
            "state": schemas.actions.StateCreate(type="RUNNING").json_dict(),
        }
        response = await client.post("/flow_run_states/", json=flow_run_state_data)
        assert response.status_code == 422
        assert "value_error.missing" in response.text


class TestReadFlowRunStateById:
    async def test_read_flow_run_state(self, flow_run, client):
        # create a flow run state to read
        flow_run_state_data = {
            "flow_run_id": flow_run.id,
            "state": schemas.actions.StateCreate(type="RUNNING").json_dict(),
        }
        response = await client.post("/flow_run_states/", json=flow_run_state_data)

        # make sure we can read the state
        flow_run_state_id = response.json()["id"]
        response = await client.get(f"/flow_run_states/{flow_run_state_id}")
        assert response.status_code == 200
        assert response.json()["id"] == flow_run_state_id

    async def test_read_flow_run_state_returns_404_if_does_not_exist(self, client):
        response = await client.get(f"/flow_run_states/{uuid4()}")
        assert response.status_code == 404


class TestReadFlowRunStateByFlowRunId:
    async def test_read_flow_run_state(self, flow_run, flow_run_states, client):
        response = await client.get(f"/flow_run_states/?flow_run_id={flow_run.id}")
        assert response.status_code == 200
        response_state_ids = {state["id"] for state in response.json()}
        assert response_state_ids == set([state.id for state in flow_run_states])
