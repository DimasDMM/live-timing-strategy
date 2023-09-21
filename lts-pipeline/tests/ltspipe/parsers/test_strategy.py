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
from tests.fixtures import AUTH_KEY, REAL_API_LTS, TEST_COMPETITION_CODE

# Not useful in these unit tests, so it is empty
PARSERS_SETTINGS: Dict[ParserSettings, str] = {}


class TestStrategyPitsStatsParser:
    """Test ltspipe.parsers.websocket.StrategyPitsStatsParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions, expected_is_parsed',
        [
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=2,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
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
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_STRATEGY_PITS_STATS,
                        data=AddStrategyPitsStats(
                            competition_code=TEST_COMPETITION_CODE,
                            pit_in_id=3,
                            best_time=59500,
                            avg_time=59600,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=200000,  # competition not existing in the database
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
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
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=2,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                Notification(  # in_data
                    type=NotificationType.ADDED_PIT_IN,
                    data=PitIn(
                        id=3,
                        team_id=5,
                        driver_id=7,
                        lap=0,  # no lap defined
                        pit_time=150900,
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
                            pit_in_id=3,
                            best_time=59500,
                            avg_time=59600,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=2,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=2,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
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
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        parser = StrategyPitsStatsParser(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=in_competitions)
        out_actions, is_parsed = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
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
                f'Unknown competition with code={TEST_COMPETITION_CODE}',
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=2,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
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
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        parser = StrategyPitsStatsParser(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
