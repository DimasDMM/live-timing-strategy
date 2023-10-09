import pytest
from typing import Any, List, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
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


def _build_non_init() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('endurance_display_driver_name.txt')
    return (in_data, [], False)


def _build_init_qualy_1() -> Tuple[Message, List[Action], bool]:
    in_data = load_raw_message('init_qualy_1.txt')
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
                ParserSettings.TIMING_INTERVAL: 'c9',
                ParserSettings.TIMING_LAP: 'c10',
                ParserSettings.TIMING_PIT_TIME: 'c11',
                ParserSettings.TIMING_NUMBER_PITS: 'c12',
            },
            participants={
                'r5625': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=1,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=None,
                    position=1,
                    team_name='Team 1',
                ),
                'r5626': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=2,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5626',
                    pit_time=None,
                    position=2,
                    team_name='Team 2',
                ),
                'r5627': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=3,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5627',
                    pit_time=None,
                    position=3,
                    team_name='Team 3',
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
            parsers_settings={
                ParserSettings.TIMING_POSITION: 'c3',
                ParserSettings.TIMING_KART_NUMBER: 'c4',
                ParserSettings.TIMING_NAME: 'c5',
                ParserSettings.TIMING_LAST_TIME: 'c6',
                ParserSettings.TIMING_BEST_TIME: 'c7',
                ParserSettings.TIMING_GAP: 'c8',
                ParserSettings.TIMING_INTERVAL: 'c9',
                ParserSettings.TIMING_LAP: 'c10',
                ParserSettings.TIMING_PIT_TIME: 'c11',
                ParserSettings.TIMING_NUMBER_PITS: 'c12',
            },
            participants={
                'r5625': Participant(
                    best_time=64882,  # 1:04.882
                    driver_name=None,
                    gap=None,
                    interval=None,
                    kart_number=1,
                    laps=0,
                    last_time=65142,  # 1:05.142
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=None,
                    position=1,
                    team_name='Team 1',
                ),
                'r5626': Participant(
                    best_time=64890,  # 1:04.890
                    driver_name=None,
                    gap=None,
                    interval=None,
                    kart_number=2,
                    laps=0,
                    last_time=65460,  # 1:05.460
                    number_pits=1,
                    participant_code='r5626',
                    pit_time=None,
                    position=2,
                    team_name='Team 2',
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
                    team_name='Team 3',
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
                value=509444,
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
                'r612': Participant(
                    best_time=65695,
                    driver_name='DRIVER 612',
                    gap=DiffLap(value=267, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=1,
                    laps=9,
                    last_time=69276,
                    number_pits=0,
                    participant_code='r612',
                    pit_time=11000,
                    position=4,
                    team_name='Team 1',
                ),
                'r617': Participant(
                    best_time=66721,
                    driver_name='DRIVER 617',
                    gap=DiffLap(value=1293, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=6,
                    laps=9,
                    last_time=66721,
                    number_pits=0,
                    participant_code='r617',
                    pit_time=11000,
                    position=27,
                    team_name='Team 2',
                ),
                'r621': Participant(
                    best_time=66216,
                    driver_name='DRIVER 621',
                    gap=DiffLap(value=788, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=10,
                    laps=9,
                    last_time=66584,
                    number_pits=0,
                    participant_code='r621',
                    pit_time=11000,
                    position=17,
                    team_name='Team 3',
                ),
                'r623': Participant(
                    best_time=65973,
                    driver_name='DRIVER 623',
                    gap=DiffLap(value=545, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=12,
                    laps=10,
                    last_time=66110,
                    number_pits=0,
                    participant_code='r623',
                    pit_time=11000,
                    position=11,
                    team_name='Team 4',
                ),
                'r624': Participant(
                    best_time=65888,
                    driver_name='DRIVER 624',
                    gap=DiffLap(value=460, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=13,
                    laps=10,
                    last_time=65987,
                    number_pits=0,
                    participant_code='r624',
                    pit_time=11000,
                    position=7,
                    team_name='Team 5',
                ),
                'r625': Participant(
                    best_time=66411,
                    driver_name='DRIVER 625',
                    gap=DiffLap(value=983, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=14,
                    laps=10,
                    last_time=66735,
                    number_pits=0,
                    participant_code='r625',
                    pit_time=11000,
                    position=21,
                    team_name='Team 6',
                ),
                'r626': Participant(
                    best_time=65428,
                    driver_name='DRIVER 626',
                    gap=None,
                    interval=None,
                    kart_number=15,
                    laps=10,
                    last_time=65428,
                    number_pits=0,
                    participant_code='r626',
                    pit_time=11000,
                    position=1,
                    team_name='Team 7',
                ),
                'r631': Participant(
                    best_time=66221,
                    driver_name='DRIVER 631',
                    gap=DiffLap(value=793, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=20,
                    laps=9,
                    last_time=67434,
                    number_pits=0,
                    participant_code='r631',
                    pit_time=11000,
                    position=18,
                    team_name='Team 8',
                ),
                'r632': Participant(
                    best_time=66416,
                    driver_name='DRIVER 632',
                    gap=DiffLap(value=988, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=21,
                    laps=9,
                    last_time=67381,
                    number_pits=0,
                    participant_code='r632',
                    pit_time=11000,
                    position=22,
                    team_name='Team 9',
                ),
                'r633': Participant(
                    best_time=65893,
                    driver_name='DRIVER 633',
                    gap=DiffLap(value=465, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=22,
                    laps=9,
                    last_time=66297,
                    number_pits=0,
                    participant_code='r633',
                    pit_time=11000,
                    position=8,
                    team_name='Team 10',
                ),
                'r634': Participant(
                    best_time=66242,
                    driver_name='DRIVER 634',
                    gap=DiffLap(value=814, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=23,
                    laps=9,
                    last_time=66242,
                    number_pits=0,
                    participant_code='r634',
                    pit_time=11000,
                    position=19,
                    team_name='Team 11',
                ),
                'r635': Participant(
                    best_time=65742,
                    driver_name='DRIVER 635',
                    gap=DiffLap(value=314, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=24,
                    laps=9,
                    last_time=87586,
                    number_pits=0,
                    participant_code='r635',
                    pit_time=11000,
                    position=5,
                    team_name='Team 12',
                ),
                'r636': Participant(
                    best_time=66051,
                    driver_name='DRIVER 636',
                    gap=DiffLap(value=623, unit=LengthUnit.MILLIS),
                    interval=None,
                    kart_number=25,
                    laps=9,
                    last_time=66238,
                    number_pits=0,
                    participant_code='r636',
                    pit_time=11000,
                    position=13,
                    team_name='Team 13',
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
            parsers_settings={
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
            },
            participants={
                'r5625': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=41,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5625',
                    pit_time=0,
                    position=1,
                    team_name='Team 1',
                ),
                'r5626': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=42,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5626',
                    pit_time=0,
                    position=2,
                    team_name='Team 2',
                ),
                'r5627': Participant(
                    best_time=0,
                    driver_name=None,
                    kart_number=43,
                    gap=None,
                    interval=None,
                    last_time=0,
                    laps=0,
                    number_pits=0,
                    participant_code='r5627',
                    pit_time=0,
                    position=3,
                    team_name='Team 3',
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
            _build_non_init(),
            _build_init_qualy_1(),
            _build_init_qualy_2(),
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
        parser = InitialDataParser(
            info=CompetitionInfo(
                id=1,
                competition_code=TEST_COMPETITION_CODE,
                parser_settings={},
                drivers=[],
                teams=[],
            ),
        )
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    def test_parse_wrong_headers(self) -> None:
        """Test method parse with unexpected messages."""
        in_data = load_raw_message('wrong_headers.txt')
        parser = InitialDataParser(
            info=CompetitionInfo(
                id=1,
                competition_code=TEST_COMPETITION_CODE,
                parser_settings={},
                drivers=[],
                teams=[],
            ),
        )
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert (str(e) == 'Cannot parse column 8 of headers '
                          '(timing-gap != timing-number-pits).')
