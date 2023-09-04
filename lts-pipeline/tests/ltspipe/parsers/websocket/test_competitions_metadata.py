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
        'in_competitions, in_data, expected_actions',
        [
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
                'unknown data input',  # in_data
                [],  # expected_actions
            ),
            (
                {},  # in_competitions
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
        parser = CompetitionMetadataRemainingParser(
            competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message(
                    'endurance_stage_remaining_time_unknown.txt'),  # in_data
                'Unknown competition metadata remaining length: dyn1|unknown|',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = CompetitionMetadataRemainingParser(
            competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestCompetitionMetadataStatusParser:
    """Test ltspipe.parsers.websocket.CompetitionMetadataStatusParser."""

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_actions',
        [
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
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
            ),
            (
                {},  # in_competitions
                'unknown data input',  # in_data
                [],  # expected_actions
            ),
            (
                {},  # in_competitions
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
        parser = CompetitionMetadataStatusParser(competitions=in_competitions)
        out_actions = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    @pytest.mark.parametrize(
        'in_competitions, in_data, expected_exception',
        [
            (
                {},  # in_competitions
                load_raw_message('endurance_status_unknown.txt'),  # in_data
                'Unknown competition metadata status: unknown_status',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            in_competitions: Dict[str, CompetitionInfo],
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = CompetitionMetadataStatusParser(competitions=in_competitions)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
