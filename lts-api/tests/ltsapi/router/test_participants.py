from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, List, Type, Union

from ltsapi.main import app
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
    GetDriver,
    GetTeam,
    UpdateDriver,
    UpdateTeam,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.helpers import DatabaseTest


class TestMiscRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.misc."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        ('competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                200,  # expected_status_code
                [
                    GetTeam(
                        id=4,
                        competition_id=2,
                        participant_code='team-1',
                        name='CKM 1',
                        number=41,
                        reference_time_offset=0,
                        drivers=[],
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTeam(
                        id=5,
                        competition_id=2,
                        participant_code='team-2',
                        name='CKM 2',
                        number=42,
                        reference_time_offset=0,
                        drivers=[],
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTeam,  # expected_type
            ),
            (
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetTeam,  # expected_type
            ),
        ])
    def test_get_all_teams(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/<competition_id>/teams."""
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/teams')
        assert response.status_code == expected_status_code, response

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_models = [expected_type(**x) for x in data]
            response_list = [x.dict(exclude=self.EXCLUDE)
                             for x in response_models]
            expected_list = [x.dict(exclude=self.EXCLUDE)
                             for x in expected_response]
            assert response_list == expected_list
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.dict(exclude=self.EXCLUDE)
            expected_dict = expected_response.dict(exclude=self.EXCLUDE)
            assert response_dict == expected_dict

    @pytest.mark.parametrize(
        ('competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                AddTeam(
                    participant_code='new-team',
                    name='New Team',
                    number=101,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetTeam(
                    id=7,
                    competition_id=2,
                    participant_code='new-team',
                    name='New Team',
                    number=101,
                    reference_time_offset=0,
                    drivers=[],
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTeam,  # expected_type
            ),
            (
                2000000,  # competition_id
                AddTeam(
                    participant_code='new-team',
                    name='New Team',
                    number=101,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_team(
            self,
            competition_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/competitions/<competition_id>/teams.
        """
        response: Response = self.API.post(
            f'/v1/competitions/{competition_id}/teams',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, team_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                GetTeam(
                    id=4,
                    competition_id=2,
                    participant_code='team-1',
                    name='CKM 1',
                    number=41,
                    reference_time_offset=0,
                    drivers=[],
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTeam,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_team(
            self,
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competitions/<competition_id>/teams/<team_id>.
        """
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/teams/{team_id}')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, team_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                UpdateTeam(
                    participant_code='team-1',
                    name='CKM 1 Updated',
                    number=41,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetTeam(
                    id=4,
                    competition_id=2,
                    participant_code='team-1',
                    name='CKM 1 Updated',
                    number=41,
                    reference_time_offset=0,
                    drivers=[],
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTeam,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                UpdateTeam(
                    participant_code='team-1',
                    name='CKM 1 Updated',
                    number=41,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The team with ID=4 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # team_id
                UpdateTeam(
                    participant_code='team-1',
                    name='CKM 1 Updated',
                    number=41,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The team with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_team(
            self,
            competition_id: int,
            team_id: str,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/competitions/<competition_id>/teams/<team_id>.
        """
        response: Response = self.API.put(
            f'/v1/competitions/{competition_id}/teams/{team_id}',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, team_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [
                    GetDriver(
                        id=5,
                        competition_id=2,
                        team_id=4,
                        participant_code='team-1',
                        name='CKM 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetDriver(
                        id=6,
                        competition_id=2,
                        team_id=4,
                        participant_code='team-1',
                        name='CKM 1 Driver 2',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [],
                GetDriver,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # team_id
                200,  # expected_status_code
                [],
                GetDriver,  # expected_type
            ),
        ])
    def test_get_team_drivers_by_team_id(
            self,
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competitions/<competition_id>/teams/<team_id>/drivers.
        """
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/teams/{team_id}/drivers')
        assert response.status_code == expected_status_code, response

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_models = [expected_type(**x) for x in data]
            response_list = [x.dict(exclude=self.EXCLUDE)
                             for x in response_models]
            expected_list = [x.dict(exclude=self.EXCLUDE)
                             for x in expected_response]
            assert response_list == expected_list
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.dict(exclude=self.EXCLUDE)
            expected_dict = expected_response.dict(exclude=self.EXCLUDE)
            assert response_dict == expected_dict

    @pytest.mark.parametrize(
        ('competition_id, team_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                AddDriver(
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetDriver(
                    id=11,
                    competition_id=2,
                    team_id=4,
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                AddDriver(
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # team_id
                AddDriver(
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_team_driver(
            self,
            competition_id: int,
            team_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/competitions/<competition_id>/teams/<team_id>/drivers.
        """
        response: Response = self.API.post(
            f'/v1/competitions/{competition_id}/teams/{team_id}/drivers',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, team_id, driver_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                5,  # driver_id
                200,  # expected_status_code
                GetDriver(
                    id=5,
                    competition_id=2,
                    team_id=4,
                    participant_code='team-1',
                    name='CKM 1 Driver 1',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                5,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # team_id
                5,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                2,  # competition_id
                4,  # team_id
                2000000,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_team_driver(
            self,
            competition_id: int,
            team_id: int,
            driver_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET .../<competition_id>/teams/<team_id>/drivers/<driver_id>.
        """
        url = (f'/v1/competitions/{competition_id}'
               f'/teams/{team_id}/drivers/{driver_id}')
        response: Response = self.API.get(url)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, team_id, driver_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                4,  # team_id
                5,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetDriver(
                    id=5,
                    competition_id=2,
                    team_id=4,
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                4,  # team_id
                5,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The driver with ID=5 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # team_id
                5,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The driver with ID=5 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                2,  # competition_id
                4,  # team_id
                2000000,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The driver with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_team_driver(
            self,
            competition_id: int,
            team_id: int,
            driver_id: str,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT .../<competition_id>/teams/<team_id>/drivers/<driver_id>.
        """
        url = (f'/v1/competitions/{competition_id}'
               f'/teams/{team_id}/drivers/{driver_id}')
        response: Response = self.API.put(url, json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                200,  # expected_status_code
                [
                    GetDriver(
                        id=5,
                        competition_id=2,
                        team_id=4,
                        participant_code='team-1',
                        name='CKM 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetDriver(
                        id=6,
                        competition_id=2,
                        team_id=4,
                        participant_code='team-1',
                        name='CKM 1 Driver 2',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetDriver(
                        id=7,
                        competition_id=2,
                        team_id=5,
                        participant_code='team-2',
                        name='CKM 2 Driver 1',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetDriver(
                        id=8,
                        competition_id=2,
                        team_id=5,
                        participant_code='team-2',
                        name='CKM 2 Driver 2',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                        reference_time_offset=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetDriver,  # expected_type
            ),
        ])
    def test_get_all_drivers(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competitions/<competition_id>/drivers.
        """
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/drivers')
        assert response.status_code == expected_status_code, response

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_models = [expected_type(**x) for x in data]
            response_list = [x.dict(exclude=self.EXCLUDE)
                             for x in response_models]
            expected_list = [x.dict(exclude=self.EXCLUDE)
                             for x in expected_response]
            assert response_list == expected_list
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.dict(exclude=self.EXCLUDE)
            expected_dict = expected_response.dict(exclude=self.EXCLUDE)
            assert response_dict == expected_dict

    @pytest.mark.parametrize(
        ('competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                AddDriver(
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetDriver(
                    id=11,
                    competition_id=2,
                    team_id=None,
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                AddDriver(
                    participant_code='new-driver',
                    name='New Driver',
                    number=101,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_single_driver(self,
            competition_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/competitions/<competition_id>/drivers.
        """
        response: Response = self.API.post(
            f'/v1/competitions/{competition_id}/drivers',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, driver_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                GetDriver(
                    id=5,
                    competition_id=2,
                    team_id=4,
                    participant_code='team-1',
                    name='CKM 1 Driver 1',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_single_driver(self,
            competition_id: int,
            driver_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competitions/<competition_id>/drivers/<driver_id>.
        """
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/drivers/{driver_id}')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, driver_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                5,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                200,  # expected_status_code
                GetDriver(
                    id=5,
                    competition_id=2,
                    team_id=4,
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetDriver,  # expected_type
            ),
            (
                2000000,  # competition_id
                5,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The driver with ID=5 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                2,  # competition_id
                2000000,  # driver_id
                UpdateDriver(
                    participant_code='team-1',
                    name='CKM 1 Driver 1 Updated',
                    number=41,
                    total_driving_time=0,
                    partial_driving_time=0,
                    reference_time_offset=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The driver with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_single_driver(self,
            competition_id: int,
            driver_id: str,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/competitions/<competition_id>/drivers/<driver_id>.
        """
        response: Response = self.API.put(
            f'/v1/competitions/{competition_id}/drivers/{driver_id}',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
