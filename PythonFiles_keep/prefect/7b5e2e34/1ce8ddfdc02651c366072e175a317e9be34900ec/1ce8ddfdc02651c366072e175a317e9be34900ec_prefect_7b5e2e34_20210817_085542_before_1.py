from uuid import uuid4
from prefect.orion import models, schemas


class TestCreateTaskRunState:
    async def test_create_task_run_state(self, task_run, client, session):
        task_run_state_data = {
            "task_run_id": str(task_run.id),
            "state": schemas.actions.StateCreate(type="RUNNING").dict(
                json_compatible=True
            ),
        }
        response = await client.post("/task_run_states/", json=task_run_state_data)
        assert response.status_code == 200
        assert response.json()["id"]

        task_run_state = await models.task_run_states.read_task_run_state(
            session=session, task_run_state_id=response.json()["id"]
        )
        assert task_run_state.task_run_id == task_run.id

    async def test_create_task_run_state_requires_task_run_id(
        self, task_run, client, session
    ):
        task_run_state_data = {
            "task_run_id": None,
            "state": schemas.actions.StateCreate(type="RUNNING").dict(
                json_compatible=True
            ),
        }
        response = await client.post("/task_run_states/", json=task_run_state_data)
        assert response.status_code == 422
        assert "value_error.missing" in response.text


class TestBackendCachingLogic:
    async def test_set_and_retrieve_cached_task_run_state(
        self, task_run, client, database_session
    ):
        first_task_run_state_data = schemas.actions.StateCreate(
            type="COMPLETED",
            state_details={"cache_key": "cache-hit"},
        ).dict(json_compatible=True)

        second_task_run_state_data = schemas.actions.StateCreate(
            type="RUNNING",
            state_details={"cache_key": "cache-hit"},
        ).dict(json_compatible=True)

        response = await client.post(
            f"/task_runs/{task_run.id}/set_state", json=first_task_run_state_data
        )

        cached_response = await client.post(
            f"/task_runs/{task_run.id}/set_state", json=second_task_run_state_data
        )
        assert response.status_code == 201
        assert response.json()["status"] == "ACCEPT"
        assert cached_response.status_code == 201
        assert cached_response.json()["details"]["state"]["name"] == "Cached"


class TestReadTaskRunStateById:
    async def test_read_task_run_state(self, task_run, client):
        # create a task run state to read
        task_run_state_data = {
            "task_run_id": str(task_run.id),
            "state": schemas.actions.StateCreate(type="RUNNING").dict(
                json_compatible=True
            ),
        }
        response = await client.post("/task_run_states/", json=task_run_state_data)

        # make sure we can read the state
        task_run_state_id = response.json()["id"]
        response = await client.get(f"/task_run_states/{task_run_state_id}")
        assert response.status_code == 200
        assert response.json()["id"] == task_run_state_id

    async def test_read_task_run_state_returns_404_if_does_not_exist(self, client):
        response = await client.get(f"/task_run_states/{uuid4()}")
        assert response.status_code == 404


class TestReadTaskRunStateByTaskRunId:
    async def test_read_task_run_state(self, task_run, task_run_states, client):
        response = await client.get(
            "/task_run_states/", params=dict(task_run_id=task_run.id)
        )
        assert response.status_code == 200
        response_state_ids = {state["id"] for state in response.json()}
        assert response_state_ids == set([str(state.id) for state in task_run_states])
