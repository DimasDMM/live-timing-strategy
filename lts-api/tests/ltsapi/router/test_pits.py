from datetime import datetime
from fastapi.testclient import TestClient
from httpx import Response
from pydantic import BaseModel
import pytest
from typing import Any, Dict, List, Optional, Type, Union

from ltsapi.main import app
from ltsapi.models.enum import KartStatus
from ltsapi.models.pits import (
    AddPitIn,
    AddPitOut,
    GetPitIn,
    GetPitOut,
    UpdatePitIn,
    UpdatePitInFixedKartStatus,
    UpdatePitInKartStatus,
    UpdatePitInPitTime,
    UpdatePitOut,
    UpdatePitOutFixedKartStatus,
    UpdatePitOutKartStatus,
)
from ltsapi.models.responses import Empty, ErrorResponse
from tests.fixtures import AUTH_BEARER
from tests.helpers import DatabaseTest


class TestPitsInRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.pits."""

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
                    GetPitIn(
                        id=1,
                        competition_id=2,
                        team_id=4,
                        driver_id=5,
                        lap=1,
                        pit_time=150500,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetPitIn(
                        id=2,
                        competition_id=2,
                        team_id=5,
                        driver_id=7,
                        lap=1,
                        pit_time=151000,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetPitIn(
                        id=3,
                        competition_id=2,
                        team_id=5,
                        driver_id=7,
                        lap=3,
                        pit_time=150900,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetPitIn,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetPitIn,  # expected_type
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
    def test_get_pits_in_by_competition(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/pits/in."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/in',
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
        ('headers, competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,
                AddPitIn(  # add_model
                    team_id=4,
                    driver_id=5,
                    lap=3,
                    pit_time=152000,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                200,  # expected_status_code
                GetPitIn(  # expected_response
                    id=4,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=3,
                    pit_time=152000,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                None,  # headers
                2,
                AddPitIn(  # add_model
                    team_id=4,
                    driver_id=5,
                    lap=3,
                    pit_time=152000,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_pit_in(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/pits/in."""
        response: Response = self.API.post(
            f'/v1/c/{competition_id}/pits/in',
            json=add_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, pit_in_id,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                1,  # pit_in_id
                200,  # expected_status_code
                GetPitIn(
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                1,  # pit_in_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # pit_in_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                1,  # pit_in_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_pit_in_by_id(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            pit_in_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/pits/in/<pit_in_id>.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/in/{pit_in_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('url, headers, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                '/v1/c/2/pits/in/1',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=150800,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                200,  # expected_status_code
                GetPitIn(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=1,
                    pit_time=150800,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                '/v1/c/2/pits/in/1/pit_time',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitInPitTime(  # update_data
                    pit_time=150800,
                ),
                200,  # expected_status_code
                GetPitIn(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=1,
                    pit_time=150800,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                '/v1/c/2/pits/in/1/kart_status',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitInKartStatus(  # update_data
                    kart_status=KartStatus.GOOD,
                ),
                200,  # expected_status_code
                GetPitIn(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                '/v1/c/2/pits/in/1/fixed_kart_status',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitInFixedKartStatus(  # update_data
                    fixed_kart_status=KartStatus.GOOD,
                ),
                200,  # expected_status_code
                GetPitIn(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=KartStatus.GOOD,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitIn,  # expected_type
            ),
            (
                '/v1/c/2000000/pits/in/1',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested pit-in data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                '/v1/c/2/pits/in/2000000',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested pit-in data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                '/v1/c/2/pits/in/1',  # url
                None,  # headers
                UpdatePitIn(  # update_data
                    lap=1,
                    pit_time=150500,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_pit_in(
            self,
            url: str,
            headers: Optional[Dict[str, str]],
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/c/<competition_id>/pits/in/<pit_in_id>.
        """
        response: Response = self.API.put(
            url,
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
                    GetPitIn(
                        id=1,
                        competition_id=2,
                        team_id=4,
                        driver_id=5,
                        lap=1,
                        pit_time=150500,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetPitIn,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [],
                GetPitIn,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # team_id
                200,  # expected_status_code
                [],
                GetPitIn,  # expected_type
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
    def test_get_pits_in_by_team(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/pits/in/filter/team/<team_id>."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/in/filter/team/{team_id}',
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


class TestPitsOutRouter(DatabaseTest):
    """Test endpoints of ltsapi.router.pits."""

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
                    GetPitOut(
                        id=1,
                        competition_id=2,
                        team_id=4,
                        driver_id=5,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                    GetPitOut(
                        id=2,
                        competition_id=2,
                        team_id=5,
                        driver_id=7,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetPitOut,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                200,  # expected_status_code
                [],
                GetPitOut,  # expected_type
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
    def test_get_pits_out_by_competition(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/pits/out."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/out',
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
        ('headers, competition_id, add_model, expected_status_code,'
         'expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,
                AddPitOut(  # add_model
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                200,  # expected_status_code
                GetPitOut(  # expected_response
                    id=3,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitOut,  # expected_type
            ),
            (
                None,  # headers
                2,
                AddPitOut(  # add_model
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_add_pit_out(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            add_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """Test POST /v1/c/<competition_id>/pits/out."""
        response: Response = self.API.post(
            f'/v1/c/{competition_id}/pits/out',
            json=add_model.dict(),
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('headers, competition_id, pit_out_id,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                1,  # pit_out_id
                200,  # expected_status_code
                GetPitOut(
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitOut,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                1,  # pit_out_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # pit_out_id
                200,  # expected_status_code
                Empty(),
                Empty,  # expected_type
            ),
            (
                None,  # headers
                2,  # competition_id
                1,  # pit_out_id
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_get_pit_out_by_id(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            pit_out_id: int,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test GET /v1/c/<competition_id>/pits/out/<pit_out_id>.
        """
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/out/{pit_out_id}',
            headers=headers)
        assert response.status_code == expected_status_code, response.content

        response_model = expected_type(**response.json())
        response_dict = response_model.dict(exclude=self.EXCLUDE)

        assert response_dict == expected_response.dict(exclude=self.EXCLUDE)

    @pytest.mark.parametrize(
        ('url, headers, update_model,'
         'expected_status_code, expected_response, expected_type'),
        [
            (
                '/v1/c/2/pits/out/1',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitOut(  # update_data
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                200,  # expected_status_code
                GetPitOut(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitOut,  # expected_type
            ),
            (
                '/v1/c/2/pits/out/1/kart_status',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitOutKartStatus(  # update_data
                    kart_status=KartStatus.GOOD,
                ),
                200,  # expected_status_code
                GetPitOut(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.GOOD,
                    fixed_kart_status=None,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitOut,  # expected_type
            ),
            (
                '/v1/c/2/pits/out/1/fixed_kart_status',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitOutFixedKartStatus(  # update_data
                    fixed_kart_status=KartStatus.GOOD,
                ),
                200,  # expected_status_code
                GetPitOut(  # update_model
                    id=1,
                    competition_id=2,
                    team_id=4,
                    driver_id=5,
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=KartStatus.GOOD,
                    insert_date=datetime.utcnow().timestamp(),
                    update_date=datetime.utcnow().timestamp(),
                ),
                GetPitOut,  # expected_type
            ),
            (
                '/v1/c/2000000/pits/out/1',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitOut(  # update_data
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested pit-out data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                '/v1/c/2/pits/out/2000000',  # url
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                UpdatePitOut(  # update_data
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                400,  # expected_status_code
                ErrorResponse(
                    status_code=400,
                    message='The requested pit-out data does not exist.',
                ),
                ErrorResponse,  # expected_type
            ),
            (
                '/v1/c/2/pits/out/1',  # url
                None,  # headers
                UpdatePitOut(  # update_data
                    kart_status=KartStatus.UNKNOWN,
                    fixed_kart_status=None,
                ),
                403,  # expected_status_code
                ErrorResponse(
                    message='Invalid authentication.',
                    status_code=403,
                ),
                ErrorResponse,  # expected_type
            ),
        ])
    def test_update_pit_out(
            self,
            url: str,
            headers: Optional[Dict[str, str]],
            update_model: BaseModel,
            expected_status_code: int,
            expected_response: BaseModel,
            expected_type: Type[BaseModel]) -> None:
        """
        Test PUT /v1/c/<competition_id>/pits/out/<pit_out_id>.
        """
        response: Response = self.API.put(
            url,
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
                    GetPitOut(
                        id=1,
                        competition_id=2,
                        team_id=4,
                        driver_id=5,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        insert_date=datetime.utcnow().timestamp(),
                        update_date=datetime.utcnow().timestamp(),
                    ),
                ],
                GetPitOut,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2000000,  # competition_id
                4,  # team_id
                200,  # expected_status_code
                [],
                GetPitOut,  # expected_type
            ),
            (
                {'Authorization': f'Bearer {AUTH_BEARER}'},  # headers
                2,  # competition_id
                2000000,  # team_id
                200,  # expected_status_code
                [],
                GetPitOut,  # expected_type
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
    def test_get_pits_out_by_team(
            self,
            headers: Optional[Dict[str, str]],
            competition_id: int,
            team_id: int,
            expected_status_code: int,
            expected_response: Union[List[BaseModel], BaseModel],
            expected_type: Type[BaseModel]) -> None:
        """Test GET /v1/c/<competition_id>/pits/out/filter/team/<team_id>."""
        response: Response = self.API.get(
            f'/v1/c/{competition_id}/pits/out/filter/team/{team_id}',
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
