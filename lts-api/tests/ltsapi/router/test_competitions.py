from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.competitions import (
    AddCompetition,
    AddCompetitionSettings,
    GetCompetition,
    GetCompetitionMetadata,
    GetCompetitionSettings,
    UpdateCompetitionMetadata,
    UpdateCompetitionSettings,
    UpdateStatus,
    UpdateStage,
    UpdateRemainingLength,
)
from ltsapi.models.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import TEST_COMPETITION_CODE, AUTH_BEARER
from tests.helpers import DatabaseTest


class TestCompetitionsRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.competitions."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'track': {
            'insert_date': True,
            'update_date': True,
        },
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        ('headers, expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                200,  # expected_status_code
                [
                    GetCompetition(
                        id=1,
                        track={
                            'id': 1,
                            'name': 'Karting North',
                            'insert_date': datetime.utcnow().timestamp(),
                            'update_date': datetime.utcnow().timestamp(),
                        },
                        competition_code='north-endurance-2023-02-26',
                        name='Endurance North 26-02-2023',
                        description='Endurance in Karting North',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetition(
                        id=2,
                        track={
                            'id': 1,
                            'name': 'Karting North',
                            'insert_date': datetime.utcnow().timestamp(),
                            'update_date': datetime.utcnow().timestamp(),
                        },
                        competition_code='north-endurance-2023-03-25',
                        name='Endurance North 25-03-2023',
                        description='Endurance in Karting North',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetition(
                        id=3,
                        track={
                            'id': 2,
                            'name': 'Karting South',
                            'insert_date': datetime.utcnow().timestamp(),
                            'update_date': datetime.utcnow().timestamp(),
                        },
                        competition_code='south-endurance-2023-03-26',
                        name='Endurance South 26-03-2023',
                        description='Endurance in Karting South',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetCompetition,  # expected_type
            ),
            (
                None,  # headers
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_all_competitions(
            self,
            headers: Optional[Dict[str, str]],
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c."""
        response: Response = self.API.get(
            '/v1/c',
            headers=headers)
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
        ('headers, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddCompetition(
                    track_id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    name='Sample competition',
                    description='This is a test',
                    settings=AddCompetitionSettings(
                        length=10,
                        length_unit=LengthUnit.LAPS,
                        pit_time=None,
                        min_number_pits=3,
                    ),
                ),
                200,  # expected_status_code
                GetCompetition(
                    id=4,
                    track={
                        'id': 1,
                        'name': 'Karting North',
                        'insert_date': datetime.utcnow().timestamp(),
                        'update_date': datetime.utcnow().timestamp(),
                    },
                    competition_code=TEST_COMPETITION_CODE,
                    name='Sample competition',
                    description='This is a test',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetition,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddCompetition(
                    track_id=1,
                    competition_code='north-endurance-2023-02-26',
                    name='Duplicated competition',
                    description='This is duplicated',
                    settings=AddCompetitionSettings(
                        length=10,
                        length_unit=LengthUnit.LAPS,
                        pit_time=None,
                        min_number_pits=3,
                    ),
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message=('There is already a competition with '
                             'the code "north-endurance-2023-02-26".'),
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                AddCompetition(
                    track_id=1,
                    competition_code='north-endurance-2023-02-26',
                    name='Duplicated competition',
                    description='This is duplicated',
                    settings=AddCompetitionSettings(
                        length=10,
                        length_unit=LengthUnit.LAPS,
                        pit_time=None,
                        min_number_pits=3,
                    ),
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_competition(
            self,
            headers: Optional[Dict[str, str]],
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c."""
        response: Response = self.API.post(
            '/v1/c',
            json=add_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_status_code
                GetCompetition(
                    id=2,
                    track={
                        'id': 1,
                        'name': 'Karting North',
                        'insert_date': datetime.utcnow().timestamp(),
                        'update_date': datetime.utcnow().timestamp(),
                    },
                    competition_code='north-endurance-2023-03-25',
                    name='Endurance North 25-03-2023',
                    description='Endurance in Karting North',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetition,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_competition(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_code
                GetCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=348,
                    remaining_length_unit=LengthUnit.LAPS,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_competition_metadata(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/metadata."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/metadata',
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                UpdateCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                200,  # expected_status_code
                GetCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                UpdateCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The competition with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                UpdateCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_competition_metadata(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/c/<competition_id>/metadata."""
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/metadata',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                UpdateRemainingLength(
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                200,  # expected_status_code
                GetCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                UpdateRemainingLength(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The competition with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                UpdateRemainingLength(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def update_competition_metadata_remaining_length(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/c/<competition_id>/metadata/remaining_length."""
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/metadata/remaining_length',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                UpdateStage(stage=CompetitionStage.QUALIFYING),  # update_model
                200,  # expected_status_code
                GetCompetitionMetadata(
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.QUALIFYING,
                    remaining_length=348,
                    remaining_length_unit=LengthUnit.LAPS,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                UpdateStage(stage=CompetitionStage.QUALIFYING),  # update_model
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The competition with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                UpdateStage(stage=CompetitionStage.QUALIFYING),  # update_model
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def update_competition_metadata_stage(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/c/<competition_id>/metadata/stage."""
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/metadata/stage',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                UpdateStatus(status=CompetitionStatus.FINISHED),  # update_model
                200,  # expected_status_code
                GetCompetitionMetadata(
                    status=CompetitionStatus.FINISHED,
                    stage=CompetitionStage.RACE,
                    remaining_length=348,
                    remaining_length_unit=LengthUnit.LAPS,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                UpdateStatus(status=CompetitionStatus.FINISHED),  # update_model
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The competition with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                UpdateStatus(status=CompetitionStatus.FINISHED),  # update_model
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def update_competition_metadata_status(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/c/<competition_id>/metadata/status."""
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/metadata/status',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_status_code
                [
                    GetCompetitionMetadata(
                        status=CompetitionStatus.PAUSED,
                        stage=CompetitionStage.FREE_PRACTICE,
                        remaining_length=0,
                        remaining_length_unit=LengthUnit.LAPS,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetitionMetadata(
                        status=CompetitionStatus.ONGOING,
                        stage=CompetitionStage.RACE,
                        remaining_length=350,
                        remaining_length_unit=LengthUnit.LAPS,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetitionMetadata(
                        status=CompetitionStatus.ONGOING,
                        stage=CompetitionStage.RACE,
                        remaining_length=348,
                        remaining_length_unit=LengthUnit.LAPS,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetCompetitionMetadata,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetCompetitionMetadata,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_history_competition_metadata(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/metadata/history."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/metadata/history',
            headers=headers)
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
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_status_code
                GetCompetitionSettings(
                    length=320,
                    length_unit=LengthUnit.LAPS,
                    pit_time=120000,
                    min_number_pits=4,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionSettings,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_competition_settings(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/settings."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/settings',
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, update_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                UpdateCompetitionSettings(
                    length=310,
                    length_unit=LengthUnit.LAPS,
                    pit_time=120000,
                    min_number_pits=4,
                ),
                200,  # expected_status_code
                GetCompetitionSettings(
                    length=310,
                    length_unit=LengthUnit.LAPS,
                    pit_time=120000,
                    min_number_pits=4,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetitionSettings,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                UpdateCompetitionSettings(
                    length=310,
                    length_unit=LengthUnit.LAPS,
                    pit_time=120000,
                    min_number_pits=4,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The competition with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                UpdateCompetitionSettings(
                    length=310,
                    length_unit=LengthUnit.LAPS,
                    pit_time=120000,
                    min_number_pits=4,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_competition_settings(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/c/<competition_id>/settings."""
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/settings',
            json=update_model.dict(),
            headers=headers)
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
        ('headers, competition_code, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                'north-endurance-2023-03-25',  # competition_code
                200,  # expected_status_code
                GetCompetition(
                    id=2,
                    track={
                        'id': 1,
                        'name': 'Karting North',
                        'insert_date': datetime.utcnow().timestamp(),
                        'update_date': datetime.utcnow().timestamp(),
                    },
                    competition_code='north-endurance-2023-03-25',
                    name='Endurance North 25-03-2023',
                    description='Endurance in Karting North',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetCompetition,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_code
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                'north-endurance-2023-03-25',  # competition_code
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_competition_by_code(
            self,
            headers: Optional[Dict[str, str]],
            competition_code: str,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/filter/code/<competition_code>."""
        response: Response = self.API.get(
            f'/v1/c/filter/code/{competition_code}',
            headers=headers)
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
