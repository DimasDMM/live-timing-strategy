import pytest
from typing import Any, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Team,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.timing import (
    TimingBestTimeParser,
    TimingLapParser,
    TimingLastTimeParser,
    TimingNumberPitsParser,
    TimingPitTimeParser,
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


class TestTimingBestTimeParser:
    """Test ltspipe.parsers.websocket.TimingBestTimeParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
                load_raw_message(
                    'endurance_timing_best_time.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_BEST_TIME,
                        data=UpdateTimingBestTime(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            best_time=65739,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingBestTimeParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_best_time.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingBestTimeParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingLapParser:
    """Test ltspipe.parsers.websocket.TimingLapParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
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
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingLapParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_lap.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingLapParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingLastTimeParser:
    """Test ltspipe.parsers.websocket.TimingLastTimeParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
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
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingLastTimeParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_last_time.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingLastTimeParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingNumberPitsParser:
    """Test ltspipe.parsers.websocket.TimingNumberPitsParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
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
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingNumberPitsParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_number_pits.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingNumberPitsParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestPitTimeParser:
    """Test ltspipe.parsers.websocket.pits.PitTime."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
                load_raw_message(
                    'endurance_timing_pit_time_seconds.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_PIT_TIME,
                        data=UpdateTimingPitTime(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            pit_time=10000,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
                load_raw_message(
                    'endurance_timing_pit_time_minutes.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TIMING_PIT_TIME,
                        data=UpdateTimingPitTime(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                            pit_time=70000,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingPitTimeParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_pit_time_minutes.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingPitTimeParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTimingPositionParser:
    """Test ltspipe.parsers.websocket.TimingPositionParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[
                        Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ],
                ),
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
                True,  # expected_is_parsed
            ),
            (
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
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams=[],
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TimingPositionParser(info=in_competition)
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
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams=[],
                ),
                load_raw_message(
                    'endurance_timing_position.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TimingPositionParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
