from datetime import datetime
import pytest
from typing import Optional, Tuple

from pyback.data.time import Unit
from pyback.messages import Message, MessageSource
from tests.pyback.parsers import (
    build_participant,
    load_raw_message,
    INITIAL_HEADERS,
)
from pyback.parsers.websocket import WsInitParser


TEST_COMPETITION_CODE = 'sample-competition-code'


def _build_non_init() -> Tuple[Message, Optional[Message]]:
    in_message = Message(
        competition_code=TEST_COMPETITION_CODE,
        data=load_raw_message('display_driver_name.txt'),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
    )
    out_message = None
    return (in_message, out_message)


def _build_initial_3_teams() -> Tuple[Message, Optional[Message]]:
    in_message = Message(
        competition_code=TEST_COMPETITION_CODE,
        data=load_raw_message('initial_3_teams.txt'),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
    )
    out_message = Message(
        competition_code=in_message.get_competition_code(),
        data={
            'headers': INITIAL_HEADERS,
            'participants': {
                'r5625': build_participant(
                    code='r5625', ranking=1, kart_number=1, team_name='CKM 1'),
                'r5626': build_participant(
                    code='r5626', ranking=2, kart_number=2, team_name='CKM 2'),
                'r5627': build_participant(
                    code='r5627', ranking=3, kart_number=3, team_name='CKM 3'),
            },
        },
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=in_message.get_created_at(),
        updated_at=in_message.get_updated_at(),
    )
    return (in_message, out_message)


def _build_initial_3_teams_with_times() -> Tuple[Message, Optional[Message]]:
    in_message = Message(
        competition_code=TEST_COMPETITION_CODE,
        data=load_raw_message('initial_3_teams_with_times.txt'),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
    )
    out_message = Message(
        competition_code=in_message.get_competition_code(),
        data={
            'headers': INITIAL_HEADERS,
            'participants': {
                'r5625': build_participant(
                    code='r5625',
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
                    code='r5626',
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
                    code='r5627',
                    ranking=3,
                    kart_number=3,
                    team_name='CKM 3',
                    last_lap_time=65411,  # 1:05.411
                    best_time=64941,  # 1:04.941
                    gap={'value': 1, 'unit': Unit.LAPS.value},  # 1 vuelta
                    interval={
                        'value': 12293, 'unit': Unit.MILLIS.value},  # 12.293
                    pits=2,
                    pit_time=54000,  # 54.
                ),
            },
        },
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=in_message.get_created_at(),
        updated_at=in_message.get_updated_at(),
    )
    return (in_message, out_message)


class TestWsInitParser:
    """Test pyback.parsers.websocket.WsInitParser."""

    @pytest.mark.parametrize(
        'in_message, expected_message',
        [
            _build_non_init(),
            _build_initial_3_teams(),
            _build_initial_3_teams_with_times(),
        ],
    )
    def test_parse(
            self,
            in_message: Message,
            expected_message: Optional[Message]) -> None:
        """Test method parse with correct messages."""
        parser = WsInitParser()
        out_message = parser.parse(in_message)

        if expected_message is None:
            assert out_message is None
        else:
            assert (out_message.get_competition_code()
                    == expected_message.get_competition_code())
            assert out_message.get_source() == expected_message.get_source()
            assert out_message.get_data() == expected_message.get_data()
            assert (out_message.get_created_at()
                    == expected_message.get_created_at())
            assert (out_message.get_updated_at()
                    == expected_message.get_updated_at())
            assert (out_message.get_error_description()
                    == expected_message.get_error_description())
            assert (out_message.get_error_traceback()
                    == expected_message.get_error_traceback())

    def test_parse_wrong_headers(self) -> None:
        """Test method parse with unexpected messages."""
        message = Message(
            competition_code=TEST_COMPETITION_CODE,
            data=load_raw_message('wrong_headers.txt'),
            source=MessageSource.SOURCE_WS_LISTENER,
            created_at=datetime.utcnow().timestamp(),
            updated_at=datetime.utcnow().timestamp(),
        )
        parser = WsInitParser()
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(message)
        e: Exception = e_info.value
        assert str(e) == 'Cannot parse column 8 of headers (GAP != PITS).'
