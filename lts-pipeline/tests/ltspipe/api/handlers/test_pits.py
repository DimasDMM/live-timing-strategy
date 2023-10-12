import pytest
from typing import List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.handlers.pits import (
    AddPitInHandler,
    AddPitOutHandler,
)
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    CompetitionInfo,
    PitIn,
    PitOut,
)
from ltspipe.data.enum import KartStatus
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
                [1, 'r5626', 'Team 2', 41, None],
            ],
        ),
        TableContent(
            table_name='participants_drivers',
            columns=[
                'competition_id',
                'team_id',
                'participant_code',
                'name',
                'number',
                'total_driving_time',
                'partial_driving_time',
                'reference_time_offset',
            ],
            content=[
                [
                    1,
                    1,
                    'r5625',
                    'Team 1 Driver 1',
                    41,
                    0,
                    0,
                    None,
                ],
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
                    1,  # driver_id
                    1,  # position
                    61000,  # last_time
                    51000,  # best_time
                    3,  # lap
                    None,  # gap
                    None,  # gap_unit
                    0,  # interval
                    'millis',  # interval_unit
                    'qualifying',  # stage
                    0,  # pit_time
                    'good',  # kart_status
                    None,  # fixed_kart_status
                    2,  # number_pits
                ],
                [
                    1,  # competition_id
                    2,  # team_id
                    None,  # driver_id
                    2,  # position
                    62000,  # last_time
                    52000,  # best_time
                    3,  # lap
                    None,  # gap
                    None,  # gap_unit
                    0,  # interval
                    'millis',  # interval_unit
                    'qualifying',  # stage
                    0,  # pit_time
                    'bad',  # kart_status
                    'good',  # fixed_kart_status
                    1,  # number_pits
                ],
            ],
        ),
    ]


class TestAddPitInHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, add_data,'
         'expected_notification, expected_database'),
        [
            (
                # Case: add pit-in to team with driver
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
                AddPitIn(  # add_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=1,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=1,
                        driver_id=1,
                        team_id=1,
                        lap=3,
                        pit_time=0,
                        kart_status=KartStatus.GOOD,
                        fixed_kart_status=None,
                        has_pit_out=False,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='timing_pits_in',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'lap',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                            ],
                            content=[
                                [1, 1, 1, 3, 0, 'good', None],
                            ],
                        ),
                    ],
                ),
            ),
            (
                # Case: add pit-in to team with no driver
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
                AddPitIn(  # add_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=2,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=1,
                        driver_id=None,
                        team_id=2,
                        lap=3,
                        pit_time=0,
                        kart_status=KartStatus.BAD,
                        fixed_kart_status=KartStatus.GOOD,
                        has_pit_out=False,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='timing_pits_in',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'lap',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                            ],
                            content=[
                                [1, 2, None, 3, 0, 'bad', 'good'],
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
            add_data: AddPitIn,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # Handle method
        handler = AddPitInHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(add_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestAddPitOutHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, add_data,'
         'expected_notification, expected_database'),
        [
            (
                # Case: Add a pit-out and link it with the previous pit-in
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content() + [
                        TableContent(
                            table_name='timing_pits_in',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'lap',
                                'pit_time',
                                'kart_status',
                                'fixed_kart_status',
                            ],
                            content=[
                                [1, 2, None, 3, 0, 'good', None],
                            ],
                        ),
                    ],
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                AddPitOut(  # add_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=2,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADDED_PIT_OUT,
                    data=PitOut(
                        id=1,
                        driver_id=None,
                        team_id=2,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='timing_pits_out',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'kart_status',
                                'fixed_kart_status',
                            ],
                            content=[
                                [1, 2, None, 'unknown', None],
                            ],
                        ),
                        TableContent(
                            table_name='timing_pits_in_out',
                            columns=['pit_in_id', 'pit_out_id'],
                            content=[[1, 1]],
                        ),
                    ],
                ),
            ),
            (
                # Case: Add a single pit-out
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
                AddPitOut(  # add_data
                    competition_code=TEST_COMPETITION_CODE,
                    team_id=2,
                ),
                Notification(  # expected_notification
                    type=NotificationType.ADDED_PIT_OUT,
                    data=PitOut(
                        id=1,
                        driver_id=None,
                        team_id=2,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
                        TableContent(
                            table_name='timing_pits_out',
                            columns=[
                                'competition_id',
                                'team_id',
                                'driver_id',
                                'kart_status',
                                'fixed_kart_status',
                            ],
                            content=[
                                [1, 2, None, 'unknown', None],
                            ],
                        ),
                        TableContent(
                            table_name='timing_pits_in_out',
                            columns=['pit_in_id', 'pit_out_id'],
                            content=[],
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
            add_data: AddPitOut,
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # Handle method
        handler = AddPitOutHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(add_data)
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())
