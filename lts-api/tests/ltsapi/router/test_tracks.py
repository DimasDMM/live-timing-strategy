from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.tracks import (
    AddTrack,
    GetTrack,
    UpdateTrack,
)
from ltsapi.models.responses import ErrorResponse
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest


class TestTracksRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.tracks."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'insert_date': True,
        'update_date': True,
    }

    @pytest.mark.parametrize(
        'headers, expected_status_code, expected_response, expected_type',
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                200,  # expected_status_code
                [
                    GetTrack(
                        id=1,
                        name='Karting North',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetTrack(
                        id=2,
                        name='Karting South',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetTrack,  # expected_type
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
    def test_get_all_tracks(
            self,
            headers: Optional[Dict[str, str]],
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/tracks."""
        response: Response = self.API.get(
            '/v1/tracks',
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
        ('headers, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddTrack(
                    name='Test Track',
                ),
                200,  # expected_status_code
                GetTrack(
                    id=3,
                    name='Test Track',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTrack,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                AddTrack(
                    name='Karting North',
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
                AddTrack(
                    name='Test Track',
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_track(
            self,
            headers: Optional[Dict[str, str]],
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/tracks."""
        response: Response = self.API.post(
            '/v1/tracks',
            json=add_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, track_id, update_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # track_id
                UpdateTrack(
                    name='Karting South - Updated',
                ),
                200,  # expected_status_code
                GetTrack(
                    id=2,
                    name='Karting South - Updated',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetTrack,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # track_id
                UpdateTrack(
                    name='Unknown Track',
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The track with ID=2000000 does not exist.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                None,  # headers
                2,  # track_id
                UpdateTrack(
                    name='Karting South - Updated',
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_track(
            self,
            headers: Optional[Dict[str, str]],
            track_id: int,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/tracks/<track_id>."""
        response: Response = self.API.put(
            f'/v1/tracks/{track_id}',
            json=update_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
