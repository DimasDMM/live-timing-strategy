from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.enum import (
    CompetitionStage,
    KartStatus,
    LengthUnit,
)
from ltsapi.models.timing import (
    GetTiming,
    UpdateTiming,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest


class TestTimingRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.timing."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_status_code
                [
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=58800,
                        best_time=58800,
                        lap=2,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=5,
                        driver_id=7,
                        participant_code='team-2',
                        position=2,
                        last_time=59700,
                        best_time=59500,
                        lap=2,
                        gap=1400,
                        gap_unit=LengthUnit.MILLIS,
                        interval=1400,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.BAD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
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
    def test_get_current_global_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/timing."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/timing',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

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
        ('headers, competition_id, driver_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                GetTiming(
                    team_id=4,
                    driver_id=5,
                    participant_code='team-1',
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                    number_pits=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # driver_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                5,  # driver_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_current_driver_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            driver_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/timing/drivers/<driver_id>.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/timing/drivers/{driver_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, driver_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                [
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=0,
                        best_time=0,
                        lap=0,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=59000,
                        best_time=59000,
                        lap=1,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=58800,
                        best_time=58800,
                        lap=2,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                5,  # driver_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # driver_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                5,  # driver_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_history_driver_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            driver_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/timing/drivers/<driver_id>/history.
        """
        url = (f'/v1/c/{competition_id}/'
               f'timing/drivers/{driver_id}/history')
        response: Response = self.API.get(
            url,
            headers=headers)
        assert response.status_code == expected_status_code, response.content

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
        ('headers, competition_id, team_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                GetTiming(
                    team_id=4,
                    driver_id=5,
                    participant_code='team-1',
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                    number_pits=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # team_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                4,  # team_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_current_team_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/timing/teams/<team_id>.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/timing/teams/{team_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, team_id, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                4,  # team_id
                UpdateTiming(
                    driver_id=5,
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=KartStatus.BAD,
                    number_pits=0,
                ),
                200,  # expected_status_code
                GetTiming(
                    team_id=4,
                    driver_id=5,
                    participant_code='team-1',
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=KartStatus.BAD,
                    number_pits=0,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                4,  # team_id
                UpdateTiming(
                    driver_id=5,
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=KartStatus.BAD,
                    number_pits=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested timing data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # team_id
                UpdateTiming(
                    driver_id=5,
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=KartStatus.BAD,
                    number_pits=0,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested timing data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                4,  # team_id
                UpdateTiming(
                    driver_id=5,
                    position=1,
                    last_time=58800,
                    best_time=58800,
                    lap=2,
                    gap=0,
                    gap_unit=LengthUnit.MILLIS,
                    interval=0,
                    interval_unit=LengthUnit.MILLIS,
                    stage=CompetitionStage.RACE,
                    pit_time=None,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=KartStatus.BAD,
                    number_pits=0,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_timing_by_team(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            team_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/c/<competition_id>/timing/teams/<team_id>.
        """
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/timing/teams/{team_id}',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, team_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=0,
                        best_time=0,
                        lap=0,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=59000,
                        best_time=59000,
                        lap=1,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=58800,
                        best_time=58800,
                        lap=2,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # team_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                4,  # team_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_history_team_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/timing/teams/<team_id>/history.
        """
        url = (f'/v1/c/{competition_id}/'
               f'timing/teams/{team_id}/history')
        response: Response = self.API.get(
            url,
            headers=headers)
        assert response.status_code == expected_status_code, response.content

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
                [
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=0,
                        best_time=0,
                        lap=0,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=5,
                        driver_id=7,
                        participant_code='team-2',
                        position=2,
                        last_time=0,
                        best_time=0,
                        lap=0,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=59000,
                        best_time=59000,
                        lap=1,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=5,
                        driver_id=7,
                        participant_code='team-2',
                        position=2,
                        last_time=59500,
                        best_time=59500,
                        lap=1,
                        gap=500,
                        gap_unit=LengthUnit.MILLIS,
                        interval=500,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=4,
                        driver_id=5,
                        participant_code='team-1',
                        position=1,
                        last_time=58800,
                        best_time=58800,
                        lap=2,
                        gap=0,
                        gap_unit=LengthUnit.MILLIS,
                        interval=0,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTiming(
                        team_id=5,
                        driver_id=7,
                        participant_code='team-2',
                        position=2,
                        last_time=59700,
                        best_time=59500,
                        lap=2,
                        gap=1400,
                        gap_unit=LengthUnit.MILLIS,
                        interval=1400,
                        interval_unit=LengthUnit.MILLIS,
                        stage=CompetitionStage.RACE,
                        pit_time=None,
                        kart_status=KartStatus.BAD,
                        fixed_kart_status=None,
                        number_pits=0,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTiming,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetTiming,  # expected_type
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
    def test_get_history_timing(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competition/<competition_id>/timing/history.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/timing/history',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

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
