from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Type

from ltsapi.main import app
from ltsapi.models.health import GetHealth
from ltsapi.models.auth import (
    AuthRole,
    GetAuth,
    SendAuthKey,
    ValidateAuth,
)
from ltsapi.models.responses import ErrorResponse
from tests.fixtures import AUTH_BEARER, AUTH_KEY_BATCH
from tests.helpers import DatabaseTest


class TestCompetitionsRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.competitions."""

    API = TestClient(app)
    EXCLUDE: Any = {
        'bearer': True,
    }

    def test_get_health(self) -> None:
        """Test GET /v1/health."""
        response: Response = self.API.get('/v1/health')
        assert response.status_code == 200, response

        expected_response = GetHealth(status='ok')
        response_model = GetHealth(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)
        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

    @pytest.mark.parametrize(
        'add_model, expected_status_code, expected_response, expected_type',
        [
            (
                SendAuthKey(key=AUTH_KEY_BATCH),
                200,  # expected_status_code
                GetAuth(
                    bearer=AUTH_BEARER,
                    name='Test batch',
                    role=AuthRole.BATCH,
                ),
                GetAuth,  # expected_type
            ),
            (
                SendAuthKey(key='unknown key'),
                401,  # expected_status_code
                ErrorResponse(
                    message='Invalid API key.',
                    status_code=401,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_do_auth(
            self,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/auth."""
        response: Response = self.API.post(
            '/v1/auth',
            json=add_model.model_dump())
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))

        # Bearer token is generated randomly, thus this test only checks that
        # it is set
        if isinstance(response_model, GetAuth):
            assert (response_model.bearer is not None
                    and response_model.bearer != '')

    @pytest.mark.parametrize(
        'bearer, expected_status_code, expected_response, expected_type',
        [
            (
                AUTH_BEARER,  # bearer
                200,  # expected_status_code
                ValidateAuth(  # expected_response
                    name='Test batch',
                    role=AuthRole.BATCH,
                ),
                ValidateAuth,  # expected_type
            ),
            (
                'invalid-bearer-here',  # bearer
                403,  # expected_status_code
                ErrorResponse(  # expected_response
                    status_code=403,
                    message='Invalid authentication.',
                    extra_data={},
                ),
                ErrorResponse,  # expected_type
            ),
            (
                '',  # bearer
                403,  # expected_status_code
                ErrorResponse(  # expected_response
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_validate_auth(
            self,
            bearer: str,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/auth/validate."""
        response: Response = self.API.get(
            '/v1/auth/validate',
            headers={'Authorization': f'Bearer {bearer}'})
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.model_dump(exclude=self.EXCLUDE)

        assert (response_dict
                == expected_response.model_dump(exclude=self.EXCLUDE))
