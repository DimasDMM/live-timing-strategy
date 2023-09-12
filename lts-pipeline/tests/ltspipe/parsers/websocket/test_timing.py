import pytest
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Team,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPosition,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.timing import (
    TimingLapParser,
    TimingLastTimeParser,
    TimingNumberPitsParser,
    TimingPositionParser,
)
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

PARSERS_SETTINGS = {
    ParserSettings.TIMING_POSITION: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAP: 'c6',
    ParserSettings.TIMING_LAST_TIME: 'c7',
    ParserSettings.TIMING_BEST_TIME: 'c8',
    ParserSettings.TIMING_GAP: 'c9',
    ParserSettings.TIMING_INTERVAL: 'c10',
    ParserSettings.TIMING_PIT_TIME: 'c11',
    ParserSettings.TIMING_NUMBER_PITS: 'c12',
}


class TestTimingLapParser:
    """Test ltspipe.parsers.websocket.TimingLapParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions',
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
                    'endurance_timing_lap.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_LAP,
                        data=UpdateTimingLap(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            lap=143,
                        ),
                    ),
                ],
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
            ),
        ],
    )
    def test_parse(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_actions: List[Action]) -> None:
        """Test method parse with correct messages."""
        parser = TimingLapParser(competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_timing_lap.txt'),  # in_data
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
                    'endurance_timing_lap.txt'),  # in_data
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
                    'endurance_timing_lap.txt'),  # in_data
                'Column for timing-lap not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingLapParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingLastTimeParser:
    """Test ltspipe.parsers.websocket.TimingLastTimeParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions',
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
                    'endurance_timing_last_time.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_LAST_TIME,
                        data=UpdateTimingLastTime(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            last_time=65739,
                            auto_best_time=True,
                        ),
                    ),
                ],
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
            ),
        ],
    )
    def test_parse(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_actions: List[Action]) -> None:
        """Test method parse with correct messages."""
        parser = TimingLastTimeParser(competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_timing_last_time.txt'),  # in_data
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
                    'endurance_timing_last_time.txt'),  # in_data
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
                    'endurance_timing_last_time.txt'),  # in_data
                'Column for timing-last-time not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingLastTimeParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingNumberPitsParser:
    """Test ltspipe.parsers.websocket.TimingNumberPitsParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions',
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
                    'endurance_timing_number_pits.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_NUMBER_PITS,
                        data=UpdateTimingNumberPits(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            number_pits=2,
                        ),
                    ),
                ],
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
            ),
        ],
    )
    def test_parse(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_actions: List[Action]) -> None:
        """Test method parse with correct messages."""
        parser = TimingNumberPitsParser(competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_timing_number_pits.txt'),  # in_data
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
                    'endurance_timing_number_pits.txt'),  # in_data
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
                    'endurance_timing_number_pits.txt'),  # in_data
                'Column for timing-number-pits not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingNumberPitsParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingPositionParser:
    """Test ltspipe.parsers.websocket.TimingPositionParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions',
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
                    'endurance_timing_position.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_POSITION,
                        data=UpdateTimingPosition(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            position=6,
                            auto_other_positions=True,
                        ),
                    ),
                ],
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
            ),
        ],
    )
    def test_parse(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_actions: List[Action]) -> None:
        """Test method parse with correct messages."""
        parser = TimingPositionParser(competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_timing_position.txt'),  # in_data
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
                    'endurance_timing_position.txt'),  # in_data
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
                    'endurance_timing_position.txt'),  # in_data
                'Column for timing-position not found',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingPositionParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
