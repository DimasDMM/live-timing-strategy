import pytest
from typing import Any, Dict, List

from ltspipe.api.auth import refresh_bearer
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    KartStatus,
    PitIn,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.strategy import AddStrategyPitsStats
from ltspipe.parsers.strategy import StrategyPitsStatsParser
from tests.fixtures import (
    AUTH_KEY,
    REAL_API_LTS,
    TEST_COMPETITION_CODE,
)
from tests.helpers import (
    DatabaseTest,
    DatabaseContent,
    TableContent,
)

# Not useful in these unit tests, so it is empty
PARSERS_SETTINGS: Dict[ParserSettings, str] = {}


def _build_timing_one_stint() -> DatabaseContent:
    """Build timing with a team and a single stint."""
    return DatabaseContent(
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
                        'ongoing',
                        'race',
                        3600000,
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
                        66000,  # last_time
                        65000,  # best_time
                        7,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                ],
            ),
            TableContent(
                table_name='timing_history',
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
                        67000,  # last_time
                        67000,  # best_time
                        1,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        66000,  # last_time
                        66000,  # best_time
                        2,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        68000,  # last_time
                        66000,  # best_time
                        3,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                ],
            ),
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
                    [1, 1, None, 5, 0, 'good', None],
                ],
            ),
        ],
    )


def _build_timing_two_stints() -> DatabaseContent:
    """Build timing with a team and two stints."""
    return DatabaseContent(
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
                        'ongoing',
                        'race',
                        3600000,
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
                    [1, 'r5626', 'Team 2', 42, None],
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
                        66000,  # last_time
                        65000,  # best_time
                        7,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        2,  # team_id
                        None,  # driver_id
                        2,  # position
                        66000,  # last_time
                        65000,  # best_time
                        7,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                ],
            ),
            TableContent(
                table_name='timing_history',
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
                    [  # Note: I've just added 1 record of team 2
                        1,  # competition_id
                        2,  # team_id
                        None,  # driver_id
                        2,  # position
                        66000,  # last_time
                        65000,  # best_time
                        7,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        67000,  # last_time
                        67000,  # best_time
                        1,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        66000,  # last_time
                        66000,  # best_time
                        2,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        68000,  # last_time
                        66000,  # best_time
                        3,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        63000,  # last_time
                        63000,  # best_time
                        4,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        120000,  # last_time
                        63000,  # best_time
                        5,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        69000,  # last_time
                        63000,  # best_time
                        6,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        68000,  # last_time
                        63000,  # best_time
                        7,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        67000,  # last_time
                        63000,  # best_time
                        8,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        69000,  # last_time
                        63000,  # best_time
                        9,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        68000,  # last_time
                        63000,  # best_time
                        10,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        69000,  # last_time
                        63000,  # best_time
                        11,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        67000,  # last_time
                        63000,  # best_time
                        12,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                    [
                        1,  # competition_id
                        1,  # team_id
                        None,  # driver_id
                        1,  # position
                        66000,  # last_time
                        63000,  # best_time
                        13,  # lap
                        None,  # gap
                        None,  # gap_unit
                        None,  # interval
                        None,  # interval_unit
                        'race',  # stage
                        0,  # pit_time
                        'unknown',  # kart_status
                        None,  # fixed_kart_status
                        0,  # number_pits
                    ],
                ],
            ),
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
                    [1, 1, None, 5, 0, 'good', None],
                    [1, 1, None, 13, 0, 'good', None],
                ],
            ),
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
                    [1, 1, None, 'good', None],
                ],
            ),
            TableContent(
                table_name='timing_pits_in_out',
                columns=['pit_in_id', 'pit_out_id'],
                content=[[1, 1]],
            ),
        ],
    )


class TestStrategyPitsStatsParser(DatabaseTest):
    """
    Functional test ltspipe.parsers.websocket.StrategyPitsStatsParser.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('database_content, in_competition, in_data,'
         'expected_actions, expected_is_parsed'),
        [
            (
                # Case: timing with a single stint and one team
                _build_timing_one_stint(),
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=1,
                        team_id=1,
                        driver_id=None,
                        lap=5,
                        pit_time=0,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        has_pit_out=False,
                    ),
                ),
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_STRATEGY_PITS_STATS,
                        data=AddStrategyPitsStats(
                            competition_code=TEST_COMPETITION_CODE,
                            pit_in_id=1,
                            best_time=66000,
                            avg_time=67000,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                # Case: timing with two stints for a team
                _build_timing_two_stints(),  # database_content
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=2,
                        team_id=1,
                        driver_id=None,
                        lap=14,
                        pit_time=0,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        has_pit_out=False,
                    ),
                ),
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_STRATEGY_PITS_STATS,
                        data=AddStrategyPitsStats(
                            competition_code=TEST_COMPETITION_CODE,
                            pit_in_id=2,
                            best_time=66000,
                            avg_time=67200,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                # Case: timing with a two stints and one team, but the pit-in
                # does not have a lap defined
                _build_timing_two_stints(),  # database_content
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=2,
                        team_id=1,
                        driver_id=None,
                        lap=0,  # no lap defined
                        pit_time=0,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        has_pit_out=False,
                    ),
                ),
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_STRATEGY_PITS_STATS,
                        data=AddStrategyPitsStats(
                            competition_code=TEST_COMPETITION_CODE,
                            pit_in_id=2,
                            best_time=66000,
                            avg_time=67200,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                # Case: unknown competition
                DatabaseContent(  # database_content
                    tables_content=[
                    ],
                ),
                CompetitionInfo(  # in_competition
                    id=200000,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=3,
                        team_id=5,
                        driver_id=7,
                        lap=3,
                        pit_time=150900,
                        kart_status=KartStatus.UNKNOWN,
                        fixed_kart_status=None,
                        has_pit_out=False,
                    ),
                ),
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                DatabaseContent(  # database_content
                    tables_content=[],
                ),
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                DatabaseContent(  # database_content
                    tables_content=[],
                ),
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.INIT_FINISHED,
                    data=None,
                ),
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            database_content: DatabaseContent,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        self.set_database_content(database_content)
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        parser = StrategyPitsStatsParser(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            info=in_competition)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=None,
                ),
                'Unknown data content of pit-in notification',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        parser = StrategyPitsStatsParser(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
