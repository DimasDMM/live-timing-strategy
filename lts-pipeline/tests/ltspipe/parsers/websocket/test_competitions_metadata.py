import pytest
from typing import Any, Dict, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStatus,
    CompetitionInfo,
    LengthUnit,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.competitions_metadata import (
    CompetitionMetadataRemainingParser,
    CompetitionMetadataStatusParser,
)
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

# Not useful in these unit tests, so it is empty
PARSERS_SETTINGS: Dict[ParserSettings, str] = {}


class TestCompetitionMetadataRemainingParser:
    """Test ltspipe.parsers.websocket.CompetitionMetadataRemainingParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_stage_remaining_time_countdown.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,
                        data=UpdateCompetitionMetadataRemaining(
                            competition_code=TEST_COMPETITION_CODE,
                            remaining_length={
                                'value': 10761515,
                                'unit': LengthUnit.MILLIS,
                            },
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
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_stage_remaining_time_text.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,
                        data=UpdateCompetitionMetadataRemaining(
                            competition_code=TEST_COMPETITION_CODE,
                            remaining_length={
                                'value': 1200000,
                                'unit': LengthUnit.MILLIS,
                            },
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
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_stage_remaining_time_empty.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,
                        data=UpdateCompetitionMetadataRemaining(
                            competition_code=TEST_COMPETITION_CODE,
                            remaining_length={
                                'value': 0,
                                'unit': LengthUnit.MILLIS,
                            },
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
                    teams={},
                    timing={},
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
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = CompetitionMetadataRemainingParser(
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
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_stage_remaining_time_unknown.txt'),  # in_data
                'Unknown competition metadata remaining length: dyn1|unknown|',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = CompetitionMetadataRemainingParser(
            info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestCompetitionMetadataStatusParser:
    """Test ltspipe.parsers.websocket.CompetitionMetadataStatusParser."""

    @pytest.mark.parametrize(
        'in_competition, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # in_competition
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_status_paused.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
                        data=UpdateCompetitionMetadataStatus(
                            competition_code=TEST_COMPETITION_CODE,
                            status=CompetitionStatus.PAUSED,
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
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_status_started.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
                        data=UpdateCompetitionMetadataStatus(
                            competition_code=TEST_COMPETITION_CODE,
                            status=CompetitionStatus.ONGOING,
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
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_status_finished.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
                        data=UpdateCompetitionMetadataStatus(
                            competition_code=TEST_COMPETITION_CODE,
                            status=CompetitionStatus.FINISHED,
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
                    teams={},
                    timing={},
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
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = CompetitionMetadataStatusParser(info=in_competition)
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
                    teams={},
                    timing={},
                ),
                load_raw_message('endurance_status_unknown.txt'),  # in_data
                'Unknown competition metadata status: unknown_status',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competition: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = CompetitionMetadataStatusParser(info=in_competition)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
