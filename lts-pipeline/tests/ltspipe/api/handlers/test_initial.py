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
from tests.fixtures import AUTH_KEY, REAL_API_LTS, TEST_COMPETITION_CODE
from tests.helpers import DatabaseTest, create_competition


class TestInitialDataHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.InitialDataHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('initial_data_1', 'initial_data_2', 'expected_teams_1',
         'expected_teams_2', 'expected_drivers_1', 'expected_drivers_2',
         'expected_settings_1', 'expected_settings_2',
         'expected_notification_1', 'expected_notification_2'),
        [
            (
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
                            driver_name='CKM 1 Driver 1',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=41,
                            laps=5,
                            last_time=65460,  # 1:05.460
                            number_pits=1,
                            participant_code='r5625',
                            pit_time=None,
                            position=1,
                            team_name='CKM 1',
                        ),
                        'r5626': Participant(
                            best_time=64941,  # 1:04.941
                            driver_name='CKM 2 Driver 1',
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
                            team_name='CKM 2',
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
                            driver_name='CKM 1 Driver 1',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=41,
                            laps=3,
                            last_time=61000,
                            number_pits=2,
                            participant_code='r5625',
                            pit_time=0,
                            position=1,
                            team_name='CKM 1',
                        ),
                        'r5626': Participant(
                            best_time=52000,
                            driver_name='CKM 2 Driver 2 New',
                            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                            kart_number=42,
                            laps=3,
                            last_time=62000,
                            number_pits=0,
                            participant_code='r5626',
                            pit_time=0,
                            position=2,
                            team_name='CKM 2',
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
                            team_name='CKM 3',
                        ),
                    },
                ),
                [  # expected_teams_1
                    Team(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1',
                        number=41,
                    ),
                    Team(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2',
                        number=42,
                    ),
                ],
                [  # expected_teams_2
                    Team(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1',
                        number=41,
                    ),
                    Team(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2',
                        number=42,
                    ),
                    Team(
                        id=0,
                        participant_code='r5627',
                        name='CKM 3',
                        number=43,
                    ),
                ],
                [  # expected_drivers_1
                    Driver(
                        id=0,
                        team_id=0,
                        participant_code='r5625',
                        name='CKM 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        team_id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 1',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
                [  # expected_drivers_2
                    Driver(
                        id=0,
                        team_id=0,
                        participant_code='r5625',
                        name='CKM 1 Driver 1',
                        number=41,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        team_id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 1',
                        number=42,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        team_id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 2 New',
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
                    type=NotificationType.INIT_FINISHED,
                ),
                Notification(  # expected_notification_2
                    type=NotificationType.INIT_FINISHED,
                ),
            ),
        ],
    )
    def test_handle(
            self,
            initial_data_1: InitialData,
            initial_data_2: InitialData,
            expected_teams_1: List[Team],
            expected_teams_2: List[Team],
            expected_drivers_1: List[Driver],
            expected_drivers_2: List[Driver],
            expected_settings_1: Dict[ParserSettings, str],
            expected_settings_2: Dict[ParserSettings, str],
            expected_notification_1: Notification,
            expected_notification_2: Notification) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        competition_id = create_competition(
            REAL_API_LTS, bearer=auth_data.bearer)
        competitions = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=competition_id,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }

        # First call to handle method
        handler = InitialDataHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(initial_data_1)
        info = competitions[TEST_COMPETITION_CODE]
        self._add_team_id_to_drivers(info, expected_drivers_1)
        assert ([t.dict(exclude={'id': True}) for t in info.teams]
                == [t.dict(exclude={'id': True}) for t in expected_teams_1])
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_1])
        assert info.parser_settings == expected_settings_1
        assert notification is not None
        assert notification == expected_notification_1

        # Second call to handle method
        handler = InitialDataHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        notification = handler.handle(initial_data_2)
        self._add_team_id_to_drivers(info, expected_drivers_2)
        assert ([t.dict(exclude={'id': True}) for t in info.teams]
                == [t.dict(exclude={'id': True}) for t in expected_teams_2])
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_2])
        assert info.parser_settings == expected_settings_2
        assert notification is not None
        assert notification == expected_notification_2

    def test_handle_raises_exception_id_none(self) -> None:
        """Test handle method raise exception about ID None."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        competitions = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=None,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }
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
                    best_time=59000,
                    driver_name='CKM 1 Driver 1',
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=41,
                    laps=5,
                    last_time=61000,
                    number_pits=0,
                    participant_code='r5625',
                    pits=2,
                    position=1,
                    team_name='CKM 1',
                ),
            },
        )

        # Call to handle method
        with pytest.raises(Exception) as e_info:
            handler = InitialDataHandler(
                api_url=REAL_API_LTS,
                auth_data=auth_data,
                competitions=competitions)
            handler.handle(initial_data)

        exception: Exception = e_info.value
        assert (str(exception) == 'ID of the competition cannot '
                                  f'be None: {TEST_COMPETITION_CODE}')

    def test_handle_raises_exception_unknown_team(self) -> None:
        """
        Test handle method raise exception about unkown team.

        It creates a competition without any team or driver, and tries to add
        a driver without team. It should return in an error since the driver
        needs that a team exists.
        """
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        competition_id = create_competition(
            REAL_API_LTS, bearer=auth_data.bearer)
        competitions = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=competition_id,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }
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
                    driver_name='CKM 1 Driver 1',
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
                api_url=REAL_API_LTS,
                auth_data=auth_data,
                competitions=competitions)
            handler.handle(initial_data)

        exception: Exception = e_info.value
        assert (str(exception) == 'Team with code=r5625 could not be found.')

    def _add_team_id_to_drivers(
            self, info: CompetitionInfo, drivers: List[Driver]) -> None:
        """
        Search the drivers in CompetitionInfo and add them the ID of the team.
        """
        code_to_team_id = {team.participant_code: team.id
                           for team in info.teams}
        for d in drivers:
            d.team_id = code_to_team_id[d.participant_code]
