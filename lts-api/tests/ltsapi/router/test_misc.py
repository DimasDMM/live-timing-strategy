from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.parsers import (
    AddParserSetting,
    GetParserSetting,
    UpdateParserSetting,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest


class TestMiscRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.misc."""

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
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetParserSetting,  # expected_type
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
    def test_get_all_parsers_settings(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/parsers/settings."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/parsers/settings',
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
        ('headers, competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
            (
                None,  # headers
                2,  # competition_id
                AddParserSetting(
                    name='timing-ranking',
                    value='timing-ranking-value',
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_parser_setting(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test POST /v1/c/<competition_id>/parsers/settings.
        """
        response: Response = self.API.post(
            f'/v1/c/{competition_id}/parsers/settings',
            json=add_model.model_dump(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

    @pytest.mark.parametrize(
        ('headers, competition_id, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
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
    def test_delete_parsers_settings(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test DELETE /v1/c/<competition_id>/parsers/settings.
        """
        response: Response = self.API.delete(
            f'/v1/c/{competition_id}/parsers/settings',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

    @pytest.mark.parametrize(
        ('headers, competition_id, s_name, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                'timing-gap',  # s_name
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                'timing-gap',  # s_name
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_parser_setting(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            s_name: str,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/parsers/settings/<s_name>.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/parsers/settings/{s_name}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

    @pytest.mark.parametrize(
        ('headers, competition_id, s_name, update_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
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
            (
                None,  # headers
                2,  # competition_id
                'timing-gap',  # s_name
                UpdateParserSetting(
                    name='timing-gap',
                    value='timing-gap-value-udpated',
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_parser_setting(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            s_name: str,
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/c/<competition_id>/parsers/settings/<s_name>.
        """
        response: Response = self.API.put(
            f'/v1/c/{competition_id}/parsers/settings/{s_name}',
            json=update_model.model_dump(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))
