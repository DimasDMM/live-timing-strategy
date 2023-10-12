import pytest
from typing import Any, List

from ltspipe.data.actions import Action
from ltspipe.data.competitions import (
    CompetitionInfo,
    Team,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.special import IgnoreParser
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

PARSERS_SETTINGS = {
    ParserSettings.IGNORE_1: 'c1',
    ParserSettings.IGNORE_2: 'c2',
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


class TestIgnoreParser:
    """Test ltspipe.parsers.websocket.IgnoreParser."""

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
                load_raw_message('endurance_ignore_1.txt'),  # in_data
                [],  # expected_actions
                True,  # expected_is_parsed
            ),
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
                load_raw_message('endurance_ignore_2.txt'),  # in_data
                [],  # expected_actions
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
        parser = IgnoreParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed
