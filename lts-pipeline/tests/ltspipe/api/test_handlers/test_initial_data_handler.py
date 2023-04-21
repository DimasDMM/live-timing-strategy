import os
import pytest
from typing import Dict, List

from ltspipe.api.handlers import InitialDataHandler
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
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import DatabaseTest, create_competition


class TestInitialDataHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.InitialDataHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    API_LTS = os.environ.get('API_LTS', '')

    @pytest.mark.parametrize(
        ('initial_data_1', 'initial_data_2', 'expected_teams_1',
         'expected_teams_2', 'expected_drivers_1', 'expected_drivers_2',
         'expected_settings_1', 'expected_settings_2'),
        [
            (
                InitialData(  # initial_data_1
                    competition_code=TEST_COMPETITION_CODE,
                    reference_time=None,
                    reference_current_offset=None,
                    stage=CompetitionStage.QUALIFYING,
                    status=CompetitionStatus.ONGOING,
                    remaining_length=DiffLap(
                        value=10,
                        unit=LengthUnit.LAPS,
                    ),
                    participants={
                        'r5625': Participant(
                            participant_code='r5625',
                            ranking=1,
                            kart_number=41,
                            team_name='CKM 1',
                            driver_name='CKM 1 Driver 1',
                            last_lap_time=65460,  # 1:05.460
                            best_time=64890,  # 1:04.890
                            pits=1,
                        ),
                        'r5626': Participant(
                            participant_code='r5626',
                            ranking=2,
                            kart_number=42,
                            team_name='CKM 2',
                            driver_name='CKM 2 Driver 1',
                            last_lap_time=65411,  # 1:05.411
                            best_time=64941,  # 1:04.941
                            gap=DiffLap(
                                value=1,  # 1 lap
                                unit=LengthUnit.LAPS.value,
                            ),
                            interval=DiffLap(
                                value=12293,  # 12.293
                                unit=LengthUnit.MILLIS.value,
                            ),
                            pits=2,
                            pit_time=54000,  # 54.
                        ),
                    },
                    parsers_settings={
                        ParserSettings.TIMING_RANKING: 'c3',
                        ParserSettings.TIMING_KART_NUMBER: 'c4',
                        ParserSettings.TIMING_NAME: 'c5',
                        ParserSettings.TIMING_LAST_LAP_TIME: 'c6',
                        ParserSettings.TIMING_BEST_TIME: 'c7',
                        ParserSettings.TIMING_GAP: 'c8',
                        ParserSettings.TIMING_INTERVAL: 'c9',
                        ParserSettings.TIMING_PIT_TIME: 'c10',
                        ParserSettings.TIMING_PITS: 'c11',
                    },
                ),
                InitialData(  # initial_data_2
                    competition_code=TEST_COMPETITION_CODE,
                    reference_time=None,
                    reference_current_offset=None,
                    stage=CompetitionStage.QUALIFYING,
                    status=CompetitionStatus.ONGOING,
                    remaining_length=DiffLap(
                        value=9,
                        unit=LengthUnit.LAPS,
                    ),
                    participants={
                        'r5625': Participant(
                            participant_code='r5625',
                            ranking=1,
                            kart_number=41,
                            team_name='CKM 1',
                            driver_name='CKM 1 Driver 1',
                            pits=2,
                        ),
                        'r5626': Participant(
                            participant_code='r5626',
                            ranking=2,
                            kart_number=42,
                            team_name='CKM 2',
                            driver_name='CKM 2 Driver 2 New',
                        ),
                        'r5627': Participant(
                            participant_code='r5627',
                            ranking=3,
                            kart_number=43,
                            team_name='CKM 3',
                            driver_name=None,
                        ),
                    },
                ),
                [  # expected_teams_1
                    Team(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1',
                    ),
                    Team(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2',
                    ),
                ],
                [  # expected_teams_2
                    Team(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1',
                    ),
                    Team(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2',
                    ),
                    Team(
                        id=0,
                        participant_code='r5627',
                        name='CKM 3',
                    ),
                ],
                [  # expected_drivers_1
                    Driver(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1 Driver 1',
                    ),
                    Driver(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 1',
                    ),
                ],
                [  # expected_drivers_2
                    Driver(
                        id=0,
                        participant_code='r5625',
                        name='CKM 1 Driver 1',
                    ),
                    Driver(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 1',
                    ),
                    Driver(
                        id=0,
                        participant_code='r5626',
                        name='CKM 2 Driver 2 New',
                    ),
                ],
                {  # expected_settings_1
                    ParserSettings.TIMING_RANKING: 'c3',
                    ParserSettings.TIMING_KART_NUMBER: 'c4',
                    ParserSettings.TIMING_NAME: 'c5',
                    ParserSettings.TIMING_LAST_LAP_TIME: 'c6',
                    ParserSettings.TIMING_BEST_TIME: 'c7',
                    ParserSettings.TIMING_GAP: 'c8',
                    ParserSettings.TIMING_INTERVAL: 'c9',
                    ParserSettings.TIMING_PIT_TIME: 'c10',
                    ParserSettings.TIMING_PITS: 'c11',
                },
                {},  # expected_settings_2
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
            expected_settings_2: Dict[ParserSettings, str]) -> None:
        """Test handle method."""
        competition_id = create_competition(self.API_LTS)
        competitions = {
            TEST_COMPETITION_CODE: CompetitionInfo(
                id=competition_id,
                competition_code=TEST_COMPETITION_CODE,
            ),
        }

        # First call to handle method
        handler = InitialDataHandler(
            api_url=self.API_LTS, competitions=competitions)
        handler.handle(initial_data_1)
        info = competitions[TEST_COMPETITION_CODE]
        self._add_team_id_to_drivers(info, expected_drivers_1)
        assert ([t.dict(exclude={'id': True}) for t in info.teams]
                == [t.dict(exclude={'id': True}) for t in expected_teams_1])
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_1])
        assert info.parser_settings == expected_settings_1

        # Scond call to handle method
        handler = InitialDataHandler(
            api_url=self.API_LTS, competitions=competitions)
        handler.handle(initial_data_2)
        self._add_team_id_to_drivers(info, expected_drivers_2)
        assert ([t.dict(exclude={'id': True}) for t in info.teams]
                == [t.dict(exclude={'id': True}) for t in expected_teams_2])
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_2])
        assert info.parser_settings == expected_settings_2

    def test_handle_raises_exception_id_none(self) -> None:
        """Test handle method raise exception about ID None."""
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
                    participant_code='r5625',
                    ranking=1,
                    kart_number=41,
                    team_name='CKM 1',
                    driver_name='CKM 1 Driver 1',
                    pits=2,
                ),
            },
        )

        # Call to handle method
        with pytest.raises(Exception) as e_info:
            handler = InitialDataHandler(
                api_url=self.API_LTS, competitions=competitions)
            handler.handle(initial_data)

        exception: Exception = e_info.value
        assert (str(exception) == 'ID of the competition cannot '
                                  f'be None: {TEST_COMPETITION_CODE}')

    def test_handle_raises_exception_unknown_team(self) -> None:
        """Test handle method raise exception about unkown team."""
        competition_id = create_competition(self.API_LTS)
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
                    participant_code='r5625',
                    ranking=1,
                    kart_number=41,
                    team_name=None,
                    driver_name='CKM 1 Driver 1',
                    pits=2,
                ),
            },
        )

        # Call to handle method
        with pytest.raises(Exception) as e_info:
            handler = InitialDataHandler(
                api_url=self.API_LTS, competitions=competitions)
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
