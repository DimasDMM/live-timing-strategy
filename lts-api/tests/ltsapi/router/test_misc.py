from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import List, Type, Union

from ltsapi.main import app
from ltsapi.models.parsers import (
    AddParserSetting,
    GetParserSetting,
    UpdateParserSetting,
)
from ltsapi.models.tracks import (
    AddTrack,
    GetTrack,
    UpdateTrack,
)
from ltsapi.models.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import DatabaseTest


class TestMiscRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.misc."""

    API = TestClient(app)
    EXCLUDE = {
        'track': {
            'insert_date': True,
            'update_date': True,
        },
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
                    GetParserSetting(
                        name='timing-best-time',
                        value='timing-best-time-value',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetParserSetting(
                        name='timing-gap',
                        value='timing-gap-value',
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetParserSetting,  # expected_type
            ),
            (
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetParserSetting,  # expected_type
            ),
        ])
    def test_get_all_parsers_settings(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/competitions/{competition_id}/parsers/settings."""
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/parsers/settings')
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
        ('competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                AddParserSetting(
                    name='timing-ranking',
                    value='timing-ranking-value',
                ),
                200,  # expected_status_code
                GetParserSetting(
                    name='timing-ranking',
                    value='timing-ranking-value',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetParserSetting,  # expected_type
            ),
            (
                2000000,  # competition_id
                AddParserSetting(
                    name='timing-ranking',
                    value='timing-ranking-value',
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
    def test_add_parser_setting(
            self,
            competition_id: int,
            add_model: AddParserSetting,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/competitions/{competition_id}/parsers/settings.
        """
        response: Response = self.API.post(
            f'/v1/competitions/{competition_id}/parsers/settings',
            json=add_model.dict())
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
                Empty(),
                Empty,  # expected_type
            ),
            (
                2000000,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_delete_parsers_settings(
            self,
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test DELETE /v1/competitions/{competition_id}/parsers/settings.
        """
        response: Response = self.API.delete(
            f'/v1/competitions/{competition_id}/parsers/settings')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, s_name, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                'timing-gap',  # s_name
                200,  # expected_status_code
                GetParserSetting(
                    name='timing-gap',
                    value='timing-gap-value',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetParserSetting,  # expected_type
            ),
            (
                2000000,  # competition_id
                'timing-gap',  # s_name
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
        ])
    def test_get_parser_setting(
            self,
            competition_id: int,
            s_name: str,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/competitions/{competition_id}/parsers/settings/{s_name}.
        """
        response: Response = self.API.get(
            f'/v1/competitions/{competition_id}/parsers/settings/{s_name}')
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('competition_id, s_name, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                2,  # competition_id
                'timing-gap',  # s_name
                UpdateParserSetting(
                    name='timing-gap',
                    value='timing-gap-value-udpated',
                ),
                200,  # expected_status_code
                GetParserSetting(
                    name='timing-gap',
                    value='timing-gap-value-udpated',
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetParserSetting,  # expected_type
            ),
            (
                2,  # competition_id
                'unknown-name',  # s_name
                UpdateParserSetting(
                    name='unknown-name',
                    value='unknown-name-value',
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
                2000000,  # competition_id
                'timing-gap',  # s_name
                UpdateParserSetting(
                    name='timing-gap',
                    value='timing-gap-value-udpated',
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
    def test_update_parser_setting(
            self,
            competition_id: int,
            s_name: str,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/competitions/{competition_id}/parsers/settings/{s_name}.
        """
        response: Response = self.API.put(
            f'/v1/competitions/{competition_id}/parsers/settings/{s_name}',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        'expected_status_code, expected_response, expected_type',
        [
            (
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
        ])
    def test_get_all_tracks(
            self,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/tracks."""
        response: Response = self.API.get('/v1/tracks')
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
        ('add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
        ])
    def test_add_track(
            self,
            add_model: AddTrack,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/tracks.
        """
        response: Response = self.API.post(
            f'/v1/tracks',
            json=add_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('track_id, update_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
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
        ])
    def test_update_track(
            self,
            track_id: int,
            update_model: UpdateTrack,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """
        Test POUT /v1/tracks/{track_id}.
        """
        response: Response = self.API.put(
            f'/v1/tracks/{track_id}',
            json=update_model.dict())
        assert response.status_code == expected_status_code, response

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)
