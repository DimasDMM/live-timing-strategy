import pytest
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    AddPitIn,
    AddPitOut,
    CompetitionInfo,
    Team,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.pits import (
    PitInParser,
    PitOutParser,
)
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

# Not useful in these unit tests, so it is empty
PARSERS_SETTINGS: Dict[ParserSettings, str] = {}


class TestPitInParser:
    """Test ltspipe.parsers.websocket.pits.PitIn."""

    @pytest.mark.parametrize(
        'info, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
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
                load_raw_message('endurance_pit_in.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_PIT_IN,
                        data=AddPitIn(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = PitInParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'info, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_pit_in.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = PitInParser(info=info)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestPitOutParser:
    """Test ltspipe.parsers.websocket.pits.PitOut."""

    @pytest.mark.parametrize(
        'info, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
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
                load_raw_message('endurance_pit_out.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.ADD_PIT_OUT,
                        data=AddPitOut(
                            competition_code=TEST_COMPETITION_CODE,
                            team_id=1,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = PitOutParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'info, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_pit_out.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = PitOutParser(info=info)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
