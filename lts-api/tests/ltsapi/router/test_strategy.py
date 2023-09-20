from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, Optional, Type

from ltsapi.main import app
from ltsapi.models.responses import Empty
from ltsapi.models.strategy import (
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
        """Test POST /v1/strategy/pits/stats."""
        response: Response = self.API.post(
            '/v1/strategy/pits/stats',
            json=add_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

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
        """Test POST /v1/strategy/pits/stats/<pit_in_id>."""
        response: Response = self.API.get(
            f'/v1/strategy/pits/stats/{pit_in_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
