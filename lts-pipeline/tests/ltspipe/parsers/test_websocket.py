import pytest
from typing import Any, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    DiffLap,
)
from ltspipe.data.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
    ParserSettings,
)
from ltspipe.messages import Message
from tests.helpers import (
    build_participant,
    load_raw_message,
)
from ltspipe.parsers.websocket import WsInitParser


INITIAL_PARSERS_SETTINGS = {
    ParserSettings.TIMING_RANKING: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAST_LAP_TIME: 'c6',
    ParserSettings.TIMING_BEST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_PIT_TIME: 'c10',
    ParserSettings.TIMING_PITS: 'c11',
}
TEST_COMPETITION_CODE = 'sample-competition-code'


def _build_non_init() -> Tuple[Message, Optional[List[Action]]]:
    in_data = load_raw_message('display_driver_name.txt')
    return (in_data, [])


def _build_initial_3_teams() -> Tuple[Message, List[Action]]:
    in_data = load_raw_message('initial_3_teams.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data={
            'reference_time': 0,
            'reference_current_offset': 0,
            'stage': CompetitionStage.QUALIFYING.value,
            'status': CompetitionStatus.ONGOING.value,
            'remaining_length': DiffLap(
                value=1200000,
                unit=LengthUnit.MILLIS,
            ),
            'parsers_settings': INITIAL_PARSERS_SETTINGS,
            'participants': {
                'r5625': build_participant(
                    participant_code='r5625',
                    ranking=1,
                    kart_number=1,
                    team_name='CKM 1',
                ),
                'r5626': build_participant(
                    participant_code='r5626',
                    ranking=2,
                    kart_number=2,
                    team_name='CKM 2',
                ),
                'r5627': build_participant(
                    participant_code='r5627',
                    ranking=3,
                    kart_number=3,
                    team_name='CKM 3',
                ),
            },
        },
    )
    return (in_data, [out_action])


def _build_initial_3_teams_with_times() -> Tuple[Message, List[Action]]:
    in_data = load_raw_message('initial_3_teams_with_times.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data={
            'reference_time': 0,
            'reference_current_offset': 0,
            'stage': CompetitionStage.QUALIFYING.value,
            'status': CompetitionStatus.ONGOING.value,
            'remaining_length': DiffLap(
                value=1200000,
                unit=LengthUnit.MILLIS,
            ),
            'parsers_settings': INITIAL_PARSERS_SETTINGS,
            'participants': {
                'r5625': build_participant(
                    participant_code='r5625',
                    ranking=1,
                    kart_number=1,
                    team_name='CKM 1',
                    last_lap_time=65142,  # 1:05.142
                    best_time=64882,  # 1:04.882
                    gap=None,
                    interval=None,
                    pits=None,
                    pit_time=None,
                ),
                'r5626': build_participant(
                    participant_code='r5626',
                    ranking=2,
                    kart_number=2,
                    team_name='CKM 2',
                    last_lap_time=65460,  # 1:05.460
                    best_time=64890,  # 1:04.890
                    gap=None,
                    interval=None,
                    pits=1,
                    pit_time=None,
                ),
                'r5627': build_participant(
                    participant_code='r5627',
                    ranking=3,
                    kart_number=3,
                    team_name='CKM 3',
                    last_lap_time=65411,  # 1:05.411
                    best_time=64941,  # 1:04.941
                    gap={'value': 1, 'unit': LengthUnit.LAPS.value},  # 1 vuelta
                    interval={
                        'value': 12293,  # 12.293
                        'unit': LengthUnit.MILLIS.value,
                    },
                    pits=2,
                    pit_time=54000,  # 54.
                ),
            },
        },
    )
    return (in_data, [out_action])


class TestWsInitParser:
    """Test ltspipe.parsers.websocket.WsInitParser."""

    @pytest.mark.parametrize(
        'in_data, expected_actions',
        [
            _build_non_init(),
            _build_initial_3_teams(),
            _build_initial_3_teams_with_times(),
        ],
    )
    def test_parse(
            self,
            in_data: Any,
            expected_actions: List[Action]) -> None:
        """Test method parse with correct messages."""
        parser = WsInitParser()
        out_actions = parser.parse(in_data)
        assert ([x.dict() for x in out_actions]
                == [x.dict() for x in expected_actions])

    def test_parse_wrong_headers(self) -> None:
        """Test method parse with unexpected messages."""
        in_data = load_raw_message('wrong_headers.txt')
        parser = WsInitParser()
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert (str(e) == 'Cannot parse column 8 of headers '
                          '(timing-gap != timing-pits).')
