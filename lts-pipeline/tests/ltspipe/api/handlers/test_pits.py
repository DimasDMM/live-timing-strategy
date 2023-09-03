import pytest

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.pits import (
    AddPitInHandler,
    AddPitOutHandler,
)
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    KartStatus,
    PitIn,
    PitOut,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, REAL_API_LTS
from tests.helpers import DatabaseTest


class TestAddPitInHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.AddPitInHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'add_data', 'expected_notification'),
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                AddPitIn(  # add_data
                    id=None,
                    competition_code='south-endurance-2023-03-26',
                    driver_id=3,
                    team_id=2,
                    lap=0,
                    pit_time=0,
                    kart_status=KartStatus.GOOD,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADD_PIT_IN,
                    data=PitIn(
                        id=0,
                        driver_id=3,
                        team_id=2,
                        lap=0,
                        pit_time=0,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            add_data: AddPitIn,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # Handle method
        handler = AddPitInHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(add_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))


class TestAddPitOutHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.AddPitOutHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'add_data', 'expected_notification'),
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                AddPitOut(  # add_data
                    id=None,
                    competition_code='south-endurance-2023-03-26',
                    driver_id=3,
                    team_id=2,
                    lap=0,
                    pit_time=0,
                    kart_status=KartStatus.GOOD,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADD_PIT_OUT,
                    data=PitOut(
                        id=0,
                        driver_id=3,
                        team_id=2,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            add_data: AddPitOut,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # Handle method
        handler = AddPitOutHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(add_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))
