from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.enum import KartStatus
from ltsapi.models.responses import Empty
from ltsapi.models.strategy import (
    AddStrategyPitsKarts,
    GetStrategyPitsKarts,
    AddStrategyPitsStats,
    GetStrategyPitsStats,
)
from ltsapi.models.responses import ErrorResponse
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest


class TestStrategyRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.strategy."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        ('headers, add_models, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                [
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.MEDIUM,
                        probability=30.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.BAD,
                        probability=40.,
                    ),
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.UNKNOWN,
                        probability=10.,
                    ),
                ],
                200,  # expected_status_code
                [
                    GetStrategyPitsKarts(
                        id=25,
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=26,
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.MEDIUM,
                        probability=30.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=27,
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.BAD,
                        probability=40.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=28,
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.UNKNOWN,
                        probability=10.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetStrategyPitsKarts,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                [
                    AddStrategyPitsKarts(
                        pit_in_id=1000000,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                    ),
                ],
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                [
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=100000,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                    ),
                ],
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='No data was inserted or updated.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                [
                    AddStrategyPitsKarts(
                        pit_in_id=4,
                        competition_id=3,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=20.,
                    ),
                ],
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_strategy_pits_karts(
            self,
            headers: Optional[Dict[str, str]],
            add_models: List[BaseModel],
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/strategy/pits/karts."""
        response: Response = self.API.post(
            '/v1/c/3/strategy/pits/karts',
            json=[x.model_dump() for x in add_models],
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_models = [expected_type(**x) for x in data]
            response_list = [x.model_dump(exclude=self.EXCLUDE)
                             for x in response_models]
            expected_list = [x.model_dump(exclude=self.EXCLUDE)
                             for x in expected_response]
            assert response_list == expected_list
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.model_dump(exclude=self.EXCLUDE)
            expected_dict = expected_response.model_dump(exclude=self.EXCLUDE)
            assert response_dict == expected_dict

    @pytest.mark.parametrize(
        ('headers, pit_in_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                3,  # pit_in_id
                200,  # expected_status_code
                [
                    GetStrategyPitsKarts(
                        id=13,
                        pit_in_id=3,
                        competition_id=2,
                        step=1,
                        kart_status=KartStatus.GOOD,
                        probability=75.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=14,
                        pit_in_id=3,
                        competition_id=2,
                        step=1,
                        kart_status=KartStatus.MEDIUM,
                        probability=5.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=15,
                        pit_in_id=3,
                        competition_id=2,
                        step=1,
                        kart_status=KartStatus.BAD,
                        probability=20.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=16,
                        pit_in_id=3,
                        competition_id=2,
                        step=1,
                        kart_status=KartStatus.UNKNOWN,
                        probability=0.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=17,
                        pit_in_id=3,
                        competition_id=2,
                        step=2,
                        kart_status=KartStatus.GOOD,
                        probability=65.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=18,
                        pit_in_id=3,
                        competition_id=2,
                        step=2,
                        kart_status=KartStatus.MEDIUM,
                        probability=3.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=19,
                        pit_in_id=3,
                        competition_id=2,
                        step=2,
                        kart_status=KartStatus.BAD,
                        probability=12.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=20,
                        pit_in_id=3,
                        competition_id=2,
                        step=2,
                        kart_status=KartStatus.UNKNOWN,
                        probability=20.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=21,
                        pit_in_id=3,
                        competition_id=2,
                        step=3,
                        kart_status=KartStatus.GOOD,
                        probability=63.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=22,
                        pit_in_id=3,
                        competition_id=2,
                        step=3,
                        kart_status=KartStatus.MEDIUM,
                        probability=2.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=23,
                        pit_in_id=3,
                        competition_id=2,
                        step=3,
                        kart_status=KartStatus.BAD,
                        probability=10.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetStrategyPitsKarts(
                        id=24,
                        pit_in_id=3,
                        competition_id=2,
                        step=3,
                        kart_status=KartStatus.UNKNOWN,
                        probability=30.,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetStrategyPitsKarts,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # pit_in_id
                200,  # expected_status_code
                [],
                GetStrategyPitsKarts,  # expected_type
            ),
            (
                None,  # headers
                2,  # pit_in_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_strategy_pits_karts_by_pit_in(
            self,
            headers: Optional[Dict[str, str]],
            pit_in_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/strategy/pits/karts/<pit_in_id>."""
        response: Response = self.API.get(
            f'/v1/c/2/strategy/pits/karts/{pit_in_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        if isinstance(expected_response, list):
            data: list = response.json()  # type: ignore
            response_models = [expected_type(**x) for x in data]
            response_list = [x.model_dump(exclude=self.EXCLUDE)
                             for x in response_models]
            expected_list = [x.model_dump(exclude=self.EXCLUDE)
                             for x in expected_response]
            assert response_list == expected_list
        else:
            response_model = expected_type(**response.json())
            response_dict = response_model.model_dump(exclude=self.EXCLUDE)
            expected_dict = expected_response.model_dump(exclude=self.EXCLUDE)
            assert response_dict == expected_dict

    @pytest.mark.parametrize(
        ('headers, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddStrategyPitsStats(
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                ),
                200,  # expected_status_code
                GetStrategyPitsStats(
                    id=2,
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetStrategyPitsStats,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddStrategyPitsStats(
                    pit_in_id=10000000,
                    best_time=59500,
                    avg_time=59800,
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
                None,  # headers
                AddStrategyPitsStats(
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_strategy_pits_stats(
            self,
            headers: Optional[Dict[str, str]],
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/strategy/pits/stats."""
        response: Response = self.API.post(
            '/v1/c/2/strategy/pits/stats',
            json=add_model.model_dump(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

    @pytest.mark.parametrize(
        ('headers, pit_in_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                3,  # pit_in_id
                200,  # expected_status_code
                GetStrategyPitsStats(
                    id=1,
                    pit_in_id=3,
                    best_time=59500,
                    avg_time=59800,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetStrategyPitsStats,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # pit_in_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # pit_in_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_strategy_pits_stats_by_pit_in(
            self,
            headers: Optional[Dict[str, str]],
            pit_in_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/strategy/pits/stats/<pit_in_id>."""
        response: Response = self.API.get(
            f'/v1/c/2/strategy/pits/stats/{pit_in_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))
