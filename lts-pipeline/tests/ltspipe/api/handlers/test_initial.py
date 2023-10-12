import pytest
from typing import Dict, List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.handlers.initial import InitialDataHandler
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    Driver,
    InitialData,
    Participant,
    Team,
)
from ltspipe.data.enum import (
    LengthUnit,
    ParserSettings,
)
from ltspipe.data.notifications import Notification, NotificationType
from tests.fixtures import AUTH_KEY, API_LTS, TEST_COMPETITION_CODE
from tests.helpers import (
    DatabaseTest,
    DatabaseContent,
    TableContent,
)


class TestInitialDataHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.InitialDataHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, in_competition, initial_data_1, initial_data_2,'
         'expected_teams_1, expected_teams_2, expected_drivers_1,'
         'expected_drivers_2, expected_settings_1, expected_settings_2,'
         'expected_notification_1, expected_notification_2, expected_database'),
        [
            (
                DatabaseContent(  # database_content
                    tables_content=[
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
                    ],
                ),
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                InitialData(  # initial_data_1
                    competition_code=TEST_COMPETITION_CODE,
                    stage=CompetitionStage.QUALIFYING,
                    status=CompetitionStatus.ONGOING,
                    remaining_length=DiffLap(
                        value=10,
                        unit=LengthUnit.LAPS,
                    ),
                    participants={
                        'r5625': Participant(
                            best_time=64890,  # 1:04.890
                            driver_name='Team 1 Driver 1',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=41,
                            laps=5,
                            last_time=65460,  # 1:05.460
                            number_pits=1,
                            participant_code='r5625',
                            pit_time=None,
                            position=1,
                            team_name='Team 1',
                        ),
                        'r5626': Participant(
                            best_time=64941,  # 1:04.941
                            driver_name='Team 2 Driver 1',
                            gap=DiffLap(
                                value=1,  # 1 lap
                                unit=LengthUnit.LAPS.value,
                            ),
                            interval=DiffLap(
                                value=12293,  # 12.293
                                unit=LengthUnit.MILLIS.value,
                            ),
                            kart_number=42,
                            laps=5,
                            last_time=65411,  # 1:05.411
                            number_pits=2,
                            participant_code='r5626',
                            pit_time=54000,  # 54.
                            position=2,
                            team_name='Team 2',
                        ),
                    },
                    parsers_settings={
                        ParserSettings.TIMING_POSITION: 'c3',
                        ParserSettings.TIMING_KART_NUMBER: 'c4',
                        ParserSettings.TIMING_NAME: 'c5',
                        ParserSettings.TIMING_LAST_TIME: 'c6',
                        ParserSettings.TIMING_BEST_TIME: 'c7',
                        ParserSettings.TIMING_GAP: 'c8',
                        ParserSettings.TIMING_INTERVAL: 'c9',
                        ParserSettings.TIMING_PIT_TIME: 'c10',
                        ParserSettings.TIMING_NUMBER_PITS: 'c11',
                    },
                ),
                InitialData(  # initial_data_2
                    competition_code=TEST_COMPETITION_CODE,
                    stage=CompetitionStage.QUALIFYING,
                    status=CompetitionStatus.ONGOING,
                    remaining_length=DiffLap(
                        value=9,
                        unit=LengthUnit.LAPS,
                    ),
                    participants={
                        'r5625': Participant(
                            best_time=51000,
                            driver_name='Team 1 Driver 1',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=41,
                            laps=3,
                            last_time=61000,
                            number_pits=2,
                            participant_code='r5625',
                            pit_time=0,
                            position=1,
                            team_name='Team 1',
                        ),
                        'r5626': Participant(
                            best_time=52000,
                            driver_name='Team 2 Driver 2 New',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=42,
                            laps=3,
                            last_time=62000,
                            number_pits=0,
                            participant_code='r5626',
                            pit_time=0,
                            position=2,
                            team_name='Team 2',
                        ),
                        'r5627': Participant(
                            best_time=53000,
                            driver_name=None,
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=43,
                            laps=3,
                            last_time=63000,
                            number_pits=0,
                            participant_code='r5627',
                            pit_time=0,
                            position=3,
                            team_name='Team 3',
                        ),
                    },
                ),
                [  # expected_teams_1
                    Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1',
                        number=41,
                    ),
                    Team(
                        id=2,
                        participant_code='r5626',
                        name='Team 2',
                        number=42,
                    ),
                ],
                [  # expected_teams_2
                    Team(
                        id=1,
                        participant_code='r5625',
                        name='Team 1',
                        number=41,
                    ),
                    Team(
                        id=2,
                        participant_code='r5626',
                        name='Team 2',
                        number=42,
                    ),
                    Team(
                        id=3,
                        participant_code='r5627',
                        name='Team 3',
                        number=43,
                    ),
                ],
                [  # expected_drivers_1
                    Driver(
                        id=1,
                        team_id=1,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=2,
                        team_id=2,
                        participant_code='r5626',
                        name='Team 2 Driver 1',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
                [  # expected_drivers_2
                    Driver(
                        id=1,
                        team_id=0,
                        participant_code='r5625',
                        name='Team 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=2,
                        team_id=2,
                        participant_code='r5626',
                        name='Team 2 Driver 1',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=3,
                        team_id=0,
                        participant_code='r5626',
                        name='Team 2 Driver 2 New',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
                {  # expected_settings_1
                    ParserSettings.TIMING_POSITION: 'c3',
                    ParserSettings.TIMING_KART_NUMBER: 'c4',
                    ParserSettings.TIMING_NAME: 'c5',
                    ParserSettings.TIMING_LAST_TIME: 'c6',
                    ParserSettings.TIMING_BEST_TIME: 'c7',
                    ParserSettings.TIMING_GAP: 'c8',
                    ParserSettings.TIMING_INTERVAL: 'c9',
                    ParserSettings.TIMING_PIT_TIME: 'c10',
                    ParserSettings.TIMING_NUMBER_PITS: 'c11',
                },
                {},  # expected_settings_2
                Notification(  # expected_notification_1
                    type=NotificationType.INITIALIZED_COMPETITION,
                ),
                Notification(  # expected_notification_2
                    type=NotificationType.INITIALIZED_COMPETITION,
                ),
                DatabaseContent(  # expected_database
                    tables_content=[
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
                                    'ongoing',
                                    'qualifying',
                                    9,
                                    'laps',
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
                                [1, 'r5626', 'Team 2', 42, None],
                                [1, 'r5627', 'Team 3', 43, None],
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
                                    0,  # gap
                                    'millis',  # gap_unit
                                    0,  # interval
                                    'millis',  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    2,  # number_pits
                                ],
                                [
                                    1,  # competition_id
                                    2,  # team_id
                                    3,  # driver_id
                                    2,  # position
                                    62000,  # last_time
                                    52000,  # best_time
                                    3,  # lap
                                    0,  # gap
                                    'millis',  # gap_unit
                                    0,  # interval
                                    'millis',  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    0,  # number_pits
                                ],
                                [
                                    1,  # competition_id
                                    3,  # team_id
                                    None,  # driver_id
                                    3,  # position
                                    63000,  # last_time
                                    53000,  # best_time
                                    3,  # lap
                                    0,  # gap
                                    'millis',  # gap_unit
                                    0,  # interval
                                    'millis',  # interval_unit
                                    'qualifying',  # stage
                                    0,  # pit_time
                                    'unknown',  # kart_status
                                    None,  # fixed_kart_status
                                    0,  # number_pits
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
            in_competition: CompetitionInfo,
            initial_data_1: InitialData,
            initial_data_2: InitialData,
            expected_teams_1: List[Team],
            expected_teams_2: List[Team],
            expected_drivers_1: List[Driver],
            expected_drivers_2: List[Driver],
            expected_settings_1: Dict[ParserSettings, str],
            expected_settings_2: Dict[ParserSettings, str],
            expected_notification_1: Notification,
            expected_notification_2: Notification,
            expected_database: DatabaseContent) -> None:
        """Test handle method."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        # First call to handle method
        handler = InitialDataHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=in_competition)
        notification = handler.handle(initial_data_1)
        self._add_team_id_to_drivers(in_competition, expected_drivers_1)
        assert ([t.model_dump() for _, t in in_competition.teams.items()]
                == [t.model_dump() for t in expected_teams_1])
        assert ([d.model_dump() for d in in_competition.drivers]
                == [d.model_dump() for d in expected_drivers_1])
        assert in_competition.parser_settings == expected_settings_1
        assert notification is not None
        assert notification == expected_notification_1

        # Second call to handle method
        handler = InitialDataHandler(
            api_url=API_LTS,
            auth_data=auth_data,
            info=in_competition)
        notification = handler.handle(initial_data_2)
        self._add_team_id_to_drivers(in_competition, expected_drivers_2)
        assert ([t.model_dump() for _, t in in_competition.teams.items()]
                == [t.model_dump() for t in expected_teams_2])
        assert ([d.model_dump() for d in in_competition.drivers]
                == [d.model_dump() for d in expected_drivers_2])
        assert in_competition.parser_settings == expected_settings_2
        assert notification is not None
        assert notification == expected_notification_2

        # Validate database content
        query = expected_database.to_query()
        assert (self.get_database_content(query).model_dump()
                == expected_database.model_dump())

    @pytest.mark.parametrize(
        'database_content, in_competition',
        [
            (
                DatabaseContent(  # database_content
                    tables_content=[
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
                    ],
                ),
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
            ),
        ],
    )
    def test_handle_raises_exception_unknown_team(
            self,
            database_content: DatabaseContent,
            in_competition: CompetitionInfo) -> None:
        """
        Test handle method raise LtsError about unkown team.

        It creates a competition without any team or driver, and tries to add
        a driver without team. It should return in an error since the driver
        needs that a team exists.
        """
        self.set_database_content(database_content)
        auth_data = refresh_bearer(API_LTS, AUTH_KEY)

        initial_data = InitialData(
            competition_code=TEST_COMPETITION_CODE,
            stage=CompetitionStage.QUALIFYING,
            status=CompetitionStatus.ONGOING,
            remaining_length=DiffLap(
                value=9,
                unit=LengthUnit.LAPS,
            ),
            participants={
                'r5625': Participant(
                    best_time=0,
                    driver_name='Team 1 Driver 1',
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=41,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5625',
                    pits=2,
                    position=1,
                    team_name=None,
                ),
            },
        )

        # Call to handle method
        with pytest.raises(Exception) as e_info:
            handler = InitialDataHandler(
                api_url=API_LTS,
                auth_data=auth_data,
                info=in_competition)
            handler.handle(initial_data)

        exception: Exception = e_info.value
        assert (str(exception) == 'Team with code=r5625 could not be found.')

    def _add_team_id_to_drivers(
            self, info: CompetitionInfo, drivers: List[Driver]) -> None:
        """
        Search the drivers in CompetitionInfo and add them the ID of the team.
        """
        for d in drivers:
            d.team_id = info.teams[d.participant_code].id
