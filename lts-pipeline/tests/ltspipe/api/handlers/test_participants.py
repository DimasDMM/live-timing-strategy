import pytest
from typing import List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.handlers.participants import (
    UpdateDriverHandler,
    UpdateDriverPartialDrivingTimeHandler,
    UpdateTeamHandler,
)
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateDriverPartialDrivingTime,
    UpdateTeam,
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
                    'unknown',  # kart_status
                    None,  # fixed_kart_status
                    2,  # number_pits
                ],
            ],
        ),
    ]


class TestUpdateDriverHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data, expected_drivers,'
         'expected_notification, expected_database'),
        [
            (
                # Case: update unexisting driver, so add it to the database
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateDriver(  # update_data
                    id=None,
                    competition_code=TEST_COMPETITION_CODE,
                    participant_code='r5625',
                    name='Team 1 Driver 2',
                    number=41,
                    team_id=1,
                ),
                [  # expected_drivers
                    Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=2,
                        participant_code='r5625',
                        name='Team 1 Driver 2',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_DRIVER,
                    data=Driver(
                        id=2,
                        participant_code='r5625',
                        name='Team 1 Driver 2',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                [
                                    1,
                                    1,
                                    'r5625',
                                    'Team 1 Driver 2',
                                    41,
                                    0,
                                    0,
                                    None,
                                ],
                            ],
                        ),
                    ],
                ),
            ),
            (
                # Case: update existing driver
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateDriver(  # update_data
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    participant_code='r5625',
                    name='Team 1 Driver 1 Updated',
                    number=41,
                    team_id=1,
                    total_driving_time=None,
                    partial_driving_time=70000,
                    auto_compute_total=False,
                ),
                [  # expected_drivers
                    Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1 Updated',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=70000,
                    ),
                ],
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_DRIVER,
                    data=Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1 Updated',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=70000,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                    'Team 1 Driver 1 Updated',
                                    41,
                                    0,
                                    70000,
                                    None,
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
            update_data: UpdateDriver,
            expected_drivers: List[Driver],
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # Call to handle method
        handler = UpdateDriverHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)

        assert ([d.model_dump() for d in info.drivers]
                == [d.model_dump() for d in expected_drivers])
        assert notification is not None
        assert notification.model_dump() == expected_notification.model_dump()

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateDriverPartialDrivingTimeHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data, expected_drivers,'
         'expected_notification, expected_database'),
        [
            (
                # Case: update driver partial driving time with auto-update
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateDriverPartialDrivingTime(  # update_data
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    partial_driving_time=70000,
                    auto_compute_total=True,
                ),
                [  # expected_drivers
                    Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        team_id=1,
                        total_driving_time=70000,
                        partial_driving_time=70000,
                    ),
                ],
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_DRIVER_PARTIAL_DRIVING_TIME,
                    data=Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        team_id=1,
                        total_driving_time=70000,
                        partial_driving_time=70000,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                    70000,
                                    70000,
                                    None,
                                ],
                            ],
                        ),
                    ],
                ),
            ),
            (
                # Case: update driver partial driving time without auto-update
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateDriverPartialDrivingTime(  # update_data
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    partial_driving_time=70000,
                    auto_compute_total=False,
                ),
                [  # expected_drivers
                    Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=70000,
                    ),
                ],
                Notification(  # expected_notification
                    type=NotificationType.UPDATED_DRIVER_PARTIAL_DRIVING_TIME,
                    data=Driver(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        team_id=1,
                        total_driving_time=0,
                        partial_driving_time=70000,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                    70000,
                                    None,
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
            update_data: UpdateDriver,
            expected_drivers: List[Driver],
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # Call to handle method
        handler = UpdateDriverPartialDrivingTimeHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)

        assert ([d.model_dump() for d in info.drivers]
                == [d.model_dump() for d in expected_drivers])
        assert notification is not None
        assert notification.model_dump() == expected_notification.model_dump()

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())


class TestUpdateTeamHandler(DatabaseTest):
    """
    Functional test.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, info, update_data,'
         'expected_teams, expected_notification, expected_database'),
        [
            (
                # Case: update existing team, but the ID is not given
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateTeam(  # update_data
                    id=None,
                    competition_code=TEST_COMPETITION_CODE,
                    participant_code='r5625',
                    name='Team 1 Updated',
                    number=41,
                ),
                [  # expected_teams
                    Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Updated',
                        number=41,
                    ),
                ],
                Notification(  # expected_notification_1
                    type=NotificationType.UPDATED_TEAM,
                    data=Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Updated',
                        number=41,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                [1, 'r5625', 'Team 1 Updated', 41, None],
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
                    ],
                ),
            ),
            (
                # Case: update existing team
                DatabaseContent(  # database_content
                    tables_content=_build_competition_table_content(),
                ),
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                UpdateTeam(  # update_data
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    participant_code='r5625',
                    name='Team 1 Updated',
                    number=41,
                ),
                [  # expected_teams
                    Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Updated',
                        number=41,
                    ),
                ],
                Notification(  # expected_notification_1
                    type=NotificationType.UPDATED_TEAM,
                    data=Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1 Updated',
                        number=41,
                    ),
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                [1, 'r5625', 'Team 1 Updated', 41, None],
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
                    ],
                ),
            ),
        ],
    )
    def test_handle(
            self,
            database_content: DatabaseContent,
            info: CompetitionInfo,
            update_data: UpdateTeam,
            expected_teams: List[Team],
            expected_notification: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = UpdateTeamHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=info)
        notification = handler.handle(update_data)

        assert ([t.model_dump() for _, t in info.teams.items()]
                == [t.model_dump() for t in expected_teams])
        assert notification is not None
        assert (notification.model_dump()
                == expected_notification.model_dump())

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())
