import pytest
from typing import List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.handlers.timing import (
    UpdateTimingBestTimeHandler,
    UpdateTimingLapHandler,
    UpdateTimingLastTimeHandler,
    UpdateTimingNumberPitsHandler,
    UpdateTimingPitTimeHandler,
    UpdateTimingPositionHandler,
)
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    KartStatus,
    Timing,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, API_LTS, TEST_COMPETITION_CODE
from tests.helpers import (
    DatabaseTest,
    DatabaseContent,
    TableContent,
)


def _build_competition_table_content() -> List[TableContent]:
    """Build basic list of TableContent to have a competition."""
    return [
        TableContent(
            table_name='competitions_index',
            columns=[
                'track_id',
                'competition_code',
                'name',
                'description',
            ],
            content=[
                [
                    1,
                    TEST_COMPETITION_CODE,
                    'Endurance North 26-02-2023',
                    'Endurance in Karting North',
                ],
            ],
        ),
        TableContent(
            table_name='competitions_metadata_current',
            columns=[
                'competition_id',
                'reference_time',
                'reference_current_offset',
                'status',
                'stage',
                'remaining_length',
                'remaining_length_unit',
            ],
            content=[
                [
                    1,
                    None,
                    None,
                    'paused',
                    'free-practice',
                    0,
                    'millis',
                ],
            ],
        ),
        TableContent(
            table_name='participants_teams',
            columns=[
                'competition_id',
                'participant_code',
                'name',
                'number',
                'reference_time_offset',
            ],
            content=[
                [1, 'r5625', 'Team 1', 41, None],
            ],
        ),
        TableContent(
            table_name='timing_current',
            columns=[
                'competition_id',
                'team_id',
                'driver_id',
                'position',
                'last_time',
                'best_time',
                'lap',
                'gap',
                'gap_unit',
                'interval',
                'interval_unit',
                'stage',
                'pit_time',
                'kart_status',
                'fixed_kart_status',
                'number_pits',
            ],
            content=[
                [
                    1,  # competition_id
                    1,  # team_id
                    None,  # driver_id
                    1,  # position
                    61000,  # last_time
                    59000,  # best_time
                    3,  # lap
                    None,  # gap
                    None,  # gap_unit
                    None,  # interval
                    None,  # interval_unit
                    'qualifying',  # stage
                    0,  # pit_time
                    'good',  # kart_status
                    None,  # fixed_kart_status
                    2,  # number_pits
                ],
            ],
        ),
    ]


class TestUpdateTimingBestTimeHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingBestTime(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    best_time=58000,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_BEST_TIME,
                    data=Timing(
                        best_time=58000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=61000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=0,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    61000,  # last_time
                                    58000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingBestTime,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingBestTimeHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTimingLapHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingLap(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    lap=10,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAP,
                    data=Timing(
                        best_time=59000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=10,
                        last_time=61000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=0,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    61000,  # last_time
                                    59000,  # best_time
                                    10,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingLap,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingLapHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTimingLastTimeHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingLastTime(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    last_time=58000,
                    auto_best_time=False,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAST_TIME,
                    data=Timing(
                        best_time=59000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=58000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=0,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    58000,  # last_time
                                    59000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingLastTime(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    last_time=58000,
                    auto_best_time=True,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_LAST_TIME,
                    data=Timing(
                        best_time=58000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=58000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=0,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    58000,  # last_time
                                    58000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingLastTime,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingLastTimeHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTimingNumberPitsHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingNumberPits(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    number_pits=3,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_NUMBER_PITS,
                    data=Timing(
                        best_time=59000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=61000,
                        number_pits=3,
                        participant_code='r5625',
                        pit_time=0,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    61000,  # last_time
                                    59000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    3,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingNumberPits,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingNumberPitsHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTimingPitTimeHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingPitTime(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    pit_time=16000,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_PIT_TIME,
                    data=Timing(
                        best_time=59000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=61000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=16000,
                        position=1,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    1,  # position
                                    61000,  # last_time
                                    59000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    16000,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingPitTime,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingPitTimeHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTimingPositionHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_notification, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                UpdateTimingPosition(  # update_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                    position=2,
                    auto_other_positions=True,
                ),
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_TIMING_POSITION,
                    data=Timing(
                        best_time=59000,
                        driver_id=None,
                        gap=None,
                        fixed_kart_status=None,
                        interval=None,
                        kart_status=KartStatus.GOOD,
                        lap=3,
                        last_time=61000,
                        number_pits=2,
                        participant_code='r5625',
                        pit_time=0,
                        position=2,
                        stage=CompetitionStage.QUALIFYING,
                        team_id=1,
                    ),
                ),
                DatabaseContent(  # expected_content
                    tables_content=[
                        TableContent(
                            table_name='timing_current',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'position',
                                'last_time',
                                'best_time',
                                'lap',
                                'gap',
                                'gap_unit',
                                'interval',
                                'interval_unit',
                                'stage',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                                'number_pits',
                            ],
                            content=[
                                [
                                    1,  # competition_id
                                    1,  # team_id
                                    None,  # driver_id
                                    2,  # position
                                    61000,  # last_time
                                    59000,  # best_time
                                    3,  # lap
                                    None,  # gap
                                    None,  # gap_unit
                                    None,  # interval
                                    None,  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'good',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                            ],
                        ),
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTimingPosition,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTimingPositionHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())
