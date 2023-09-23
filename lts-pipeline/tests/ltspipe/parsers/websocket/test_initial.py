import pytest
from typing import Any, List, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStage,
    CompetitionStatus,
    DiffLap,
    InitialData,
    Participant,
)
from ltspipe.data.enum import (
    LengthUnit,
    ParserSettings,
)
from ltspipe.messages import Message
from ltspipe.parsers.websocket.initial import InitialDataParser
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

QUALY_PARSERS_SETTINGS = {
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
RACE_PARSERS_SETTINGS = {
    ParserSettings.TIMING_POSITION: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAP: 'c6',
    ParserSettings.TIMING_LAST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_BEST_TIME: 'c10',
    ParserSettings.TIMING_PIT_TIME: 'c11',
    ParserSettings.TIMING_NUMBER_PITS: 'c12',
}


def _build_non_init() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('endurance_display_driver_name.txt')
    return (in_data, [], False)


def _build_init_qualy() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('init_qualy.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data=InitialData(
            competition_code=TEST_COMPETITION_CODE,
            stage=CompetitionStage.QUALIFYING.value,
            status=CompetitionStatus.PAUSED.value,
            remaining_length=DiffLap(
                value=1200000,
                unit=LengthUnit.MILLIS,
            ),
            parsers_settings=QUALY_PARSERS_SETTINGS,
            participants={
                'r5625': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=1,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=None,
                    position=1,
                    team_name='CKM 1',
                ),
                'r5626': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=2,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5626',
                    pit_time=None,
                    position=2,
                    team_name='CKM 2',
                ),
                'r5627': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=3,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5627',
                    pit_time=None,
                    position=3,
                    team_name='CKM 3',
                ),
            },
        ),
    )
    return (in_data, [out_action], True)


def _build_init_qualy_with_times() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('init_qualy_with_times.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data=InitialData(
            competition_code=TEST_COMPETITION_CODE,
            stage=CompetitionStage.QUALIFYING.value,
            status=CompetitionStatus.PAUSED.value,
            remaining_length=DiffLap(
                value=1200000,
                unit=LengthUnit.MILLIS,
            ),
            parsers_settings=QUALY_PARSERS_SETTINGS,
            participants={
                'r5625': Participant(
                    best_time=64882,  # 1:04.882
                    driver_name=None,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=1,
                    laps=0,
                    last_time=65142,  # 1:05.142
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=None,
                    position=1,
                    team_name='CKM 1',
                ),
                'r5626': Participant(
                    best_time=64890,  # 1:04.890
                    driver_name=None,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=2,
                    laps=0,
                    last_time=65460,  # 1:05.460
                    number_pits=1,
                    participant_code='r5626',
                    pit_time=None,
                    position=2,
                    team_name='CKM 2',
                ),
                'r5627': Participant(
                    best_time=64941,  # 1:04.941
                    driver_name=None,
                    gap=DiffLap(
                        value=1,  # 1 lap
                        unit=LengthUnit.LAPS.value,
                    ),
                    interval=DiffLap(
                        value=12293,  # 12.293
                        unit=LengthUnit.MILLIS.value,
                    ),
                    kart_number=3,
                    laps=0,
                    last_time=65411,  # 1:05.411
                    number_pits=2,
                    participant_code='r5627',
                    pit_time=54000,  # 54.
                    position=3,
                    team_name='CKM 3',
                ),
            },
        ),
    )
    return (in_data, [out_action], True)


def _build_init_qualy_2() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('init_qualy_2.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data=InitialData(
            competition_code=TEST_COMPETITION_CODE,
            stage=CompetitionStage.QUALIFYING.value,
            status=CompetitionStatus.PAUSED.value,
            remaining_length=DiffLap(
                value=1200000,
                unit=LengthUnit.MILLIS,
            ),
            parsers_settings={
                ParserSettings.TIMING_POSITION: 'c3',
                ParserSettings.TIMING_KART_NUMBER: 'c4',
                ParserSettings.TIMING_NAME: 'c5',
                ParserSettings.TIMING_LAST_TIME: 'c6',
                ParserSettings.TIMING_BEST_TIME: 'c7',
                ParserSettings.TIMING_GAP: 'c8',
                ParserSettings.TIMING_LAP: 'c9',
                ParserSettings.TIMING_PIT_TIME: 'c11',
                ParserSettings.TIMING_NUMBER_PITS: 'c12',
            },
            participants={
                'r5625': Participant(
                    best_time=64882,  # 1:04.882
                    driver_name=None,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=1,
                    laps=0,
                    last_time=65142,  # 1:05.142
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=None,
                    position=1,
                    team_name='CKM 1',
                ),
                'r5626': Participant(
                    best_time=64890,  # 1:04.890
                    driver_name=None,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    kart_number=2,
                    laps=0,
                    last_time=65460,  # 1:05.460
                    number_pits=1,
                    participant_code='r5626',
                    pit_time=None,
                    position=2,
                    team_name='CKM 2',
                ),
                'r5627': Participant(
                    best_time=64941,  # 1:04.941
                    driver_name=None,
                    gap=DiffLap(
                        value=1,  # 1 lap
                        unit=LengthUnit.LAPS.value,
                    ),
                    interval=DiffLap(
                        value=12293,  # 12.293
                        unit=LengthUnit.MILLIS.value,
                    ),
                    kart_number=3,
                    laps=0,
                    last_time=65411,  # 1:05.411
                    number_pits=2,
                    participant_code='r5627',
                    pit_time=54000,  # 54.
                    position=3,
                    team_name='CKM 3',
                ),
            },
        ),
    )
    return (in_data, [out_action], True)


def _build_init_race() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('init_endurance.txt')
    out_action = Action(
        type=ActionType.INITIALIZE,
        data=InitialData(
            competition_code=TEST_COMPETITION_CODE,
            stage=CompetitionStage.RACE.value,
            status=CompetitionStatus.PAUSED.value,
            remaining_length=DiffLap(
                value=10791671,
                unit=LengthUnit.MILLIS,
            ),
            parsers_settings=RACE_PARSERS_SETTINGS,
            participants={
                'r5625': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=1,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=0,
                    position=1,
                    team_name='CKM 1',
                ),
                'r5626': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=2,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5626',
                    pit_time=0,
                    position=2,
                    team_name='CKM 2',
                ),
                'r5627': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=3,
                    gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5627',
                    pit_time=0,
                    position=3,
                    team_name='CKM 3',
                ),
            },
        ),
    )
    return (in_data, [out_action], True)


class TestInitialDataParser:
    """Test ltspipe.parsers.websocket.InitialDataParser."""

    @pytest.mark.parametrize(
        'in_data, expected_actions, expected_is_parsed',
        [
            #_build_init_qualy_2(),
            _build_non_init(),
            _build_init_qualy(),
            _build_init_qualy_with_times(),
            _build_init_race(),
        ],
    )
    def test_parse(
            self,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = InitialDataParser()
        out_actions, is_parsed = parser.parse(TEST_COMPETITION_CODE, in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    def test_parse_wrong_headers(self) -> None:
        """Test method parse with unexpected messages."""
        in_data = load_raw_message('wrong_headers.txt')
        parser = InitialDataParser()
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(TEST_COMPETITION_CODE, in_data)
        e: Exception = e_info.value
        assert (str(e) == 'Cannot parse column 8 of headers '
                          '(timing-gap != timing-number-pits).')
