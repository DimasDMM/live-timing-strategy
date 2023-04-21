from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import List, Type, Union

from ltsapi.main import app
from ltsapi.models.competitions import (
    AddCompetition,
    AddCompetitionSettings,
    GetCompetition,
    GetCompetitionMetadata,
    GetCompetitionSettings,
    UpdateCompetitionMetadata,
    UpdateCompetitionSettings,
)
from ltsapi.models.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import DatabaseTest


class TestCompetitionsRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.competitions."""

    API = TestClient(app)
    EXCLUDE = {
        'track': {
            'insert_date': True,
            'update_date': True,
        },
        'insert_date': True,
        'update_date': True,
    }

    COMPETITIONS = [
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
                'update_date': '2023-04-21T09:37:11'
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
    ]

    def test_get_all_competitions(self) -> None:
        """Test GET /v1/competitions."""
        response: Response = self.API.get('/v1/competitions')
        assert response.status_code == 200

        response_models = [GetCompetition(**x) for x in response.json()]
        assert ([x.dict(exclude=self.EXCLUDE) for x in response_models]
                 == [x.dict(exclude=self.EXCLUDE) for x in self.COMPETITIONS])

    @pytest.mark.parametrize(
        ('add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
        ])
    def test_add_competition(
            self,
            add_model: AddCompetition,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/competitions."""
        response: Response = self.API.post(
            '/v1/competitions', json=add_model.dict())
        assert response.status_code == expected_status_code, response

        cls = expected_response.__class__
        response_model = cls.construct(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
                2000000,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_competition(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_id}."""
        response: Response = self.API.get(f'/v1/competitions/{competition_id}')
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
                200,  # expected_code
                GetCompetitionMetadata(
                    reference_time=0,
                    reference_current_offset=0,
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
                2000000,  # competition_id
                200,  # expected_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_competition_metadata(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_id}/metadata."""
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/metadata')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                2,  # competition_id
                UpdateCompetitionMetadata(
                    reference_time=0,
                    reference_current_offset=0,
                    status=CompetitionStatus.ONGOING,
                    stage=CompetitionStage.RACE,
                    remaining_length=347,
                    remaining_length_unit=LengthUnit.LAPS,
                ),
                200,  # expected_status_code
                GetCompetitionMetadata(
                    reference_time=0,
                    reference_current_offset=0,
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
                2000000,  # competition_id
                UpdateCompetitionMetadata(
                    reference_time=0,
                    reference_current_offset=0,
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
        ])
    def test_update_competition_metadata(
            self,
            competition_id: int,
            update_model: UpdateCompetitionMetadata,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/competitions/{competition_id}/metadata."""
        response: Response = self.API.put(
            f'/v1/competitions/{competition_id}/metadata',
            json=update_model.dict())
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
                    GetCompetitionMetadata(
                        reference_time=0,
                        reference_current_offset=0,
                        status=CompetitionStatus.PAUSED,
                        stage=CompetitionStage.FREE_PRACTICE,
                        remaining_length=0,
                        remaining_length_unit=LengthUnit.LAPS,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetitionMetadata(
                        reference_time=0,
                        reference_current_offset=0,
                        status=CompetitionStatus.ONGOING,
                        stage=CompetitionStage.RACE,
                        remaining_length=350,
                        remaining_length_unit=LengthUnit.LAPS,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetCompetitionMetadata(
                        reference_time=0,
                        reference_current_offset=0,
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
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetCompetitionMetadata,  # expected_type
            ),
        ])
    def test_get_history_competition_metadata(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_id}/metadata/history."""
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/metadata/history')
        assert response.status_code == expected_status_code, response

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_model = [expected_type(**x) for x in data]
            response_dict = [x.dict(exclude=self.EXCLUDE)
                             for x in response_model]
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == [x.dict(exclude=self.EXCLUDE)
                                 for x in expected_response]

    @pytest.mark.parametrize(
        ('competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
                2000000,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_competition_settings(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_id}/settings."""
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/settings')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, update_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
        ])
    def test_update_competition_settings(
            self,
            competition_id: int,
            update_model: UpdateCompetitionSettings,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test PUT /v1/competitions/{competition_id}/settings."""
        response: Response = self.API.put(
            f'/v1/competitions/{competition_id}/settings',
            json=update_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_code, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
                2000000,  # competition_code
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_competition_by_code(
            self,
            competition_code: str,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_code}."""
        response: Response = self.API.get(
            f'/v1/competitions/filter/code/{competition_code}')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
