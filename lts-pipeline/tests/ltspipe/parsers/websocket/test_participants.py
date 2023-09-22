import pytest
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateTeam,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.participants import (
    DriverNameParser,
    TeamNameParser,
)
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

PARSERS_SETTINGS = {
    ParserSettings.TIMING_POSITION: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAST_TIME: 'c6',
    ParserSettings.TIMING_BEST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_PIT_TIME: 'c10',
    ParserSettings.TIMING_NUMBER_PITS: 'c11',
}


class TestDriverNameParser:
    """Test ltspipe.parsers.websocket.DriverNameParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions, expected_is_parsed',
        [
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[
                            Team(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=None,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[
                            Team(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name_with_driving_time.txt'),
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=None,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[
                            Driver(
                                id=3,
                                participant_code='r5625',
                                name='DIMAS MUNOZ',
                                number=41,
                                team_id=1,
                                total_driving_time=0,
                                partial_driving_time=0,
                            ),
                        ],
                        teams=[
                            Team(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=3,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[
                            Driver(
                                id=3,
                                participant_code='r5625',
                                name='DIMAS MUNOZ',
                                number=41,
                                team_id=1,
                                total_driving_time=0,
                                partial_driving_time=0,
                            ),
                        ],
                        teams=[
                            Team(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name_with_driving_time.txt'),
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=3,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
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
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                ['unknown data format'],  # in_data
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
        parser = DriverNameParser(competitions=in_competitions)
        out_actions, is_parsed = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                f'Unknown competition with code={TEST_COMPETITION_CODE}',
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings={},
                        drivers=[],
                        teams=[],
                    ),
                },
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                'Column for timing-name not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = DriverNameParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTeamNameParser:
    """Test ltspipe.parsers.websocket.TeamNameParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions, expected_is_parsed',
        [
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[
                            Team(
                                id=1,
                                participant_code='r5625',
                                name='CKM 1',
                                number=41,
                            ),
                        ],
                    ),
                },
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TEAM,
                        data=UpdateTeam(
                            id=1,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='CKM 1',
                            number=41,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
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
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                ['unknown data format'],  # in_data
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
        parser = TeamNameParser(competitions=in_competitions)
        out_actions, is_parsed = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                f'Unknown competition with code={TEST_COMPETITION_CODE}',
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings=PARSERS_SETTINGS,
                        drivers=[],
                        teams=[],
                    ),
                },
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
            (
                {  # in_competitions
                    TEST_COMPETITION_CODE: CompetitionInfo(
                        id=1,
                        competition_code=TEST_COMPETITION_CODE,
                        parser_settings={},
                        drivers=[],
                        teams=[],
                    ),
                },
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                'Column for timing-name not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TeamNameParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
