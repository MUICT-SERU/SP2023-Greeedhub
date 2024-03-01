import datetime
from uuid import uuid4

import pendulum
import pytest
import sqlalchemy as sa

from prefect.orion import models, schemas
from prefect.orion.schemas.actions import DeploymentCreate
import prefect

services_settings = prefect.settings.orion.services


class TestCreateDeployment:
    async def test_create_deployment(self, session, client, flow):
        data = DeploymentCreate(name="My Deployment", flow_id=flow.id).dict(
            json_compatible=True
        )
        response = await client.post("/deployments/", json=data)
        assert response.status_code == 201
        assert response.json()["name"] == "My Deployment"
        deployment_id = response.json()["id"]

        deployment = await models.deployments.read_deployment(
            session=session, deployment_id=deployment_id
        )
        assert str(deployment.id) == deployment_id

    async def test_create_deployment_respects_flow_id_name_uniqueness(
        self, session, client, flow
    ):
        data = DeploymentCreate(
            name="My Deployment", flow_id=flow.id, is_schedule_active=False
        ).dict(json_compatible=True)
        response = await client.post("/deployments/", json=data)
        assert response.status_code == 201
        assert response.json()["name"] == "My Deployment"
        deployment_id = response.json()["id"]

        # post the same data
        data = DeploymentCreate(
            name="My Deployment", flow_id=flow.id, is_schedule_active=False
        ).dict(json_compatible=True)
        response = await client.post("/deployments/", json=data)
        assert response.status_code == 200
        assert response.json()["name"] == "My Deployment"
        assert response.json()["id"] == deployment_id
        assert not response.json()["is_schedule_active"]

        # post different data, upsert should be respected
        data = DeploymentCreate(
            name="My Deployment", flow_id=flow.id, is_schedule_active=True
        ).dict(json_compatible=True)
        response = await client.post("/deployments/", json=data)
        assert response.status_code == 200
        assert response.json()["name"] == "My Deployment"
        assert response.json()["id"] == deployment_id
        assert response.json()["is_schedule_active"]

    async def test_create_deployment_populates_and_returned_created(self, client, flow):
        now = pendulum.now(tz="UTC")

        data = DeploymentCreate(name="My Deployment", flow_id=flow.id).dict(
            json_compatible=True
        )
        response = await client.post("/deployments/", json=data)
        assert response.status_code == 201
        assert response.json()["name"] == "My Deployment"
        assert pendulum.parse(response.json()["created"]) >= now
        assert pendulum.parse(response.json()["updated"]) >= now

    async def test_creating_deployment_with_active_schedule_creates_runs(
        self, session, client, flow
    ):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            "/deployments/",
            json=DeploymentCreate(
                name="My Deployment",
                flow_id=flow.id,
                schedule=schemas.schedules.IntervalSchedule(
                    interval=datetime.timedelta(days=1)
                ),
            ).dict(json_compatible=True),
        )

        n_runs = await models.flow_runs.count_flow_runs(
            session, flow_filter=schemas.filters.FlowFilter(ids=[flow.id])
        )
        assert n_runs == 100

    async def test_creating_deployment_with_inactive_schedule_creates_no_runs(
        self, session, client, flow
    ):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            "/deployments/",
            json=DeploymentCreate(
                name="My Deployment",
                flow_id=flow.id,
                schedule=schemas.schedules.IntervalSchedule(
                    interval=datetime.timedelta(days=1)
                ),
                is_schedule_active=False,
            ).dict(json_compatible=True),
        )

        n_runs = await models.flow_runs.count_flow_runs(
            session, flow_filter=schemas.filters.FlowFilter(ids=[flow.id])
        )
        assert n_runs == 0

    async def test_creating_deployment_with_no_schedule_creates_no_runs(
        self, session, client, flow
    ):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            "/deployments/",
            json=DeploymentCreate(
                name="My Deployment",
                flow_id=flow.id,
                is_schedule_active=True,
            ).dict(json_compatible=True),
        )

        n_runs = await models.flow_runs.count_flow_runs(
            session, flow_filter=schemas.filters.FlowFilter(ids=[flow.id])
        )
        assert n_runs == 0


class TestReadDeployment:
    async def test_read_deployment(self, client, flow):
        # first create a deployment to read
        data = DeploymentCreate(name="My Deployment", flow_id=flow.id).dict(
            json_compatible=True
        )
        response = await client.post("/deployments/", json=data)
        deployment_id = response.json()["id"]

        # make sure we we can read the deployment correctly
        response = await client.get(f"/deployments/{deployment_id}")
        assert response.status_code == 200
        assert response.json()["id"] == deployment_id
        assert response.json()["name"] == "My Deployment"
        assert response.json()["flow_id"] == str(flow.id)

    async def test_read_deployment_returns_404_if_does_not_exist(self, client):
        response = await client.get(f"/deployments/{uuid4()}")
        assert response.status_code == 404


class TestReadDeployments:
    @pytest.fixture
    async def deployments(self, client, flow):
        await client.post(
            "/deployments/",
            json=DeploymentCreate(name="My Deployment", flow_id=flow.id).dict(
                json_compatible=True
            ),
        )
        await client.post(
            "/deployments/",
            json=DeploymentCreate(name="My Deployment 2", flow_id=flow.id).dict(
                json_compatible=True
            ),
        )

    async def test_read_deployments(self, deployments, client):
        response = await client.get("/deployments/")
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_read_deployments_applies_limit(self, deployments, client):
        response = await client.get("/deployments/", params=dict(limit=1))
        assert response.status_code == 200
        assert len(response.json()) == 1

    async def test_read_deployments_offset(self, deployments, client, session):
        response = await client.get("/deployments/", params=dict(offset=1))
        assert response.status_code == 200
        assert len(response.json()) == 1

        all_ids = await session.execute(
            sa.select(models.orm.Deployment.id).order_by(models.orm.Deployment.id)
        )
        second_id = [str(i) for i in all_ids.scalars().all()][1]
        assert response.json()[0]["id"] == second_id

    async def test_read_deployments_returns_empty_list(self, client):
        response = await client.get("/deployments/")
        assert response.status_code == 200
        assert response.json() == []


class TestDeleteDeployment:
    async def test_delete_deployment(self, client, flow):
        # first create a deployment to delete

        data = DeploymentCreate(name="My Deployment", flow_id=flow.id).dict(
            json_compatible=True
        )
        response = await client.post("/deployments/", json=data)
        deployment_id = response.json()["id"]

        # delete the deployment
        response = await client.delete(f"/deployments/{deployment_id}")
        assert response.status_code == 204

        # make sure it's deleted
        response = await client.get(f"/deployments/{deployment_id}")
        assert response.status_code == 404

    async def test_delete_deployment_returns_404_if_does_not_exist(self, client):
        response = await client.delete(f"/deployments/{uuid4()}")
        assert response.status_code == 404


class TestSetScheduleActive:
    async def test_set_schedule_inactive(self, client, deployment, session):
        assert deployment.is_schedule_active is True
        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_inactive"
        )
        assert response.status_code == 200

        await session.refresh(deployment)
        assert deployment.is_schedule_active is False

    async def test_set_schedule_inactive_can_be_called_multiple_times(
        self, client, deployment, session
    ):
        assert deployment.is_schedule_active is True
        await client.post(f"/deployments/{deployment.id}/set_schedule_inactive")
        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_inactive"
        )
        assert response.status_code == 200

        await session.refresh(deployment)
        assert deployment.is_schedule_active is False

    async def test_set_schedule_inactive_with_missing_deployment(self, client):
        response = await client.post(f"/deployments/{uuid4()}/set_schedule_inactive")
        assert response.status_code == 404

    async def test_set_schedule_active(self, client, deployment, session):
        deployment.is_schedule_active = False
        await session.commit()

        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_active"
        )
        assert response.status_code == 200

        await session.refresh(deployment)
        assert deployment.is_schedule_active is True

    async def test_set_schedule_active_can_be_called_multiple_times(
        self, client, deployment, session
    ):
        deployment.is_schedule_active = False
        await session.commit()

        await client.post(f"/deployments/{deployment.id}/set_schedule_active")
        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_active"
        )
        assert response.status_code == 200

        await session.refresh(deployment)
        assert deployment.is_schedule_active is True

    async def test_set_schedule_active_with_missing_deployment(self, client):
        response = await client.post(f"/deployments/{uuid4()}/set_schedule_active")
        assert response.status_code == 404

    async def test_set_schedule_active_schedules_runs(
        self, client, deployment, session
    ):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        deployment.is_schedule_active = False
        await session.commit()

        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_active"
        )
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 100

    async def test_set_schedule_active_doesnt_schedule_runs_if_no_schedule_set(
        self, client, deployment, session
    ):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        deployment.schedule = None
        deployment.is_schedule_active = False
        await session.commit()

        response = await client.post(
            f"/deployments/{deployment.id}/set_schedule_active"
        )
        await session.refresh(deployment)
        assert deployment.is_schedule_active is True
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0


class TestScheduleDeployment:
    async def test_schedule_deployment(self, client, session, deployment):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(f"/deployments/{deployment.id}/schedule")

        runs = await models.flow_runs.read_flow_runs(session)
        expected_dates = await deployment.schedule.get_dates(
            n=services_settings.scheduler_max_runs,
            start=pendulum.now(),
            end=pendulum.now().add(
                seconds=services_settings.scheduler_max_future_seconds
            ),
        )
        actual_dates = {r.state.state_details.scheduled_time for r in runs}
        assert actual_dates == set(expected_dates)

    async def test_schedule_deployment_max_runs(self, client, session, deployment):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            f"/deployments/{deployment.id}/schedule", json=dict(max_runs=5)
        )

        runs = await models.flow_runs.read_flow_runs(session)
        expected_dates = await deployment.schedule.get_dates(
            n=5,
            start=pendulum.now(),
            end=pendulum.now().add(
                seconds=services_settings.scheduler_max_future_seconds
            ),
        )
        actual_dates = {r.state.state_details.scheduled_time for r in runs}
        assert actual_dates == set(expected_dates)

    async def test_schedule_deployment_start_time(self, client, session, deployment):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            f"/deployments/{deployment.id}/schedule",
            json=dict(start_time=str(pendulum.now().add(days=120))),
        )

        runs = await models.flow_runs.read_flow_runs(session)
        expected_dates = await deployment.schedule.get_dates(
            n=services_settings.scheduler_max_runs,
            start=pendulum.now().add(days=120),
            end=pendulum.now().add(
                days=120, seconds=services_settings.scheduler_max_future_seconds
            ),
        )
        actual_dates = {r.state.state_details.scheduled_time for r in runs}
        assert actual_dates == set(expected_dates)

    async def test_schedule_deployment_end_time(self, client, session, deployment):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            f"/deployments/{deployment.id}/schedule",
            json=dict(end_time=str(pendulum.now().add(days=7))),
        )

        runs = await models.flow_runs.read_flow_runs(session)
        expected_dates = await deployment.schedule.get_dates(
            n=services_settings.scheduler_max_runs,
            start=pendulum.now(),
            end=pendulum.now().add(days=7),
        )
        actual_dates = {r.state.state_details.scheduled_time for r in runs}
        assert actual_dates == set(expected_dates)
        assert len(actual_dates) == 7

    async def test_schedule_deployment_backfill(self, client, session, deployment):
        n_runs = await models.flow_runs.count_flow_runs(session)
        assert n_runs == 0

        await client.post(
            f"/deployments/{deployment.id}/schedule",
            json=dict(
                start_time=str(pendulum.now().subtract(days=20)),
                end_time=str(pendulum.now()),
            ),
        )

        runs = await models.flow_runs.read_flow_runs(session)
        expected_dates = await deployment.schedule.get_dates(
            n=services_settings.scheduler_max_runs,
            start=pendulum.now().subtract(days=20),
            end=pendulum.now(),
        )
        actual_dates = {r.state.state_details.scheduled_time for r in runs}
        assert actual_dates == set(expected_dates)
        assert len(actual_dates) == 20
