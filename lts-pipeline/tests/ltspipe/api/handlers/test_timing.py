import pytest

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.timing import (
    UpdateTimingLapHandler,
    UpdateTimingLastTimeHandler,
    UpdateTimingNumberPitsHandler,
    UpdateTimingPitTimeHandler,
    UpdateTimingPositionHandler,
)
from ltspipe.data.competitions import (
    CompetitionStage,
    KartStatus,
    ParticipantTiming,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, REAL_API_LTS
from tests.helpers import DatabaseTest


class TestUpdateTimingLapHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTimingLapHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        'competition_code, update_data, expected_notification',
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingLap(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    lap=10,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAP,
                    data=ParticipantTiming(
                        best_time=59000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=10,
                        last_time=60000,
                        number_pits=0,
                        participant_code='team-1',
                        pit_time=None,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateTimingLap,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTimingLapHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))


class TestUpdateTimingLastTimeHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTimingLastTimeHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        'competition_code, update_data, expected_notification',
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingLastTime(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    last_time=58000,
                    auto_best_time=False,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAST_TIME,
                    data=ParticipantTiming(
                        best_time=59000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=1,
                        last_time=58000,
                        number_pits=0,
                        participant_code='team-1',
                        pit_time=None,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingLastTime(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    last_time=58000,
                    auto_best_time=True,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAST_TIME,
                    data=ParticipantTiming(
                        best_time=58000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=1,
                        last_time=58000,
                        number_pits=0,
                        participant_code='team-1',
                        pit_time=None,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateTimingLastTime,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTimingLastTimeHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))


class TestUpdateTimingNumberPitsHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTimingNumberPitsHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        'competition_code, update_data, expected_notification',
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingNumberPits(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    number_pits=2,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_NUMBER_PITS,
                    data=ParticipantTiming(
                        best_time=59000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=1,
                        last_time=60000,
                        number_pits=2,
                        participant_code='team-1',
                        pit_time=None,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateTimingNumberPits,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTimingNumberPitsHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))


class TestUpdateTimingPitTimeHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTimingPitTimeHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        'competition_code, update_data, expected_notification',
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingPitTime(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    pit_time=16000,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_PIT_TIME,
                    data=ParticipantTiming(
                        best_time=59000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=1,
                        last_time=60000,
                        number_pits=0,
                        participant_code='team-1',
                        pit_time=16000,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateTimingPitTime,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTimingPitTimeHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))


class TestUpdateTimingPositionHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTimingPositionHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        'competition_code, update_data, expected_notification',
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateTimingPosition(  # update_data
                    competition_code='south-endurance-2023-03-26',
                    team_id=6,
                    position=1,
                    auto_other_positions=True,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_POSITION,
                    data=ParticipantTiming(
                        best_time=59000,
                        driver_id=9,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.UNKNOWN,
                        lap=1,
                        last_time=60000,
                        number_pits=0,
                        participant_code='team-1',
                        pit_time=None,
                        position=1,
                        stage=CompetitionStage.FREE_PRACTICE,
                        team_id=6,
                    ),
                ),
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data: UpdateTimingPosition,
            expected_notification: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTimingPositionHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.dict(exclude={'data': {'id': True}})
                == expected_notification.dict(exclude={'data': {'id': True}}))
