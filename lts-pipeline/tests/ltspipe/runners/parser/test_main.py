from datetime import datetime
from pytest_mock import MockerFixture
from typing import List

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
from ltspipe.configs import ParserConfig
from ltspipe.messages import Message, MessageSource
from ltspipe.runners.parser.main import main
from tests.conftest import (
    mock_kafka_producer_builder,
    mock_kafka_consumer_builder,
)
from tests.helpers import (
    build_participant,
    load_raw_message,
)
from tests.mocks.logging import FakeLogger

COMPETITION_CODE = 'test-competition'
EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
KAFKA_SERVERS = ['localhost:9092']
WEBSOCKET_URI = 'ws://localhost:8000/ws/'

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
IN_KAFKA = [
    Message(
        competition_code=COMPETITION_CODE,
        data=load_raw_message('initial_3_teams_with_times.txt').strip(),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
        error_description=None,
        error_traceback=None,
    ).encode(),
]
OUT_EXPECTED = [
    Message(
        competition_code=COMPETITION_CODE,
        data=[
            Action(
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
                            gap={
                                'value': 1,  # 1 vuelta
                                'unit': LengthUnit.LAPS.value,
                            },
                            interval={
                                'value': 12293,  # 12.293
                                'unit': LengthUnit.MILLIS.value,
                            },
                            pits=2,
                            pit_time=54000,  # 54.
                        ),
                    },
                },
            ),
        ],
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
        error_description=None,
        error_traceback=None,
    ),
]


def test_main(mocker: MockerFixture) -> None:
    """Test main method."""
    _ = mock_kafka_consumer_builder(mocker, messages=IN_KAFKA)
    mocked_kafka = mock_kafka_producer_builder(mocker)
    fake_logger = FakeLogger()
    config = ParserConfig(
        kafka_servers=KAFKA_SERVERS,
    )

    main(config=config, logger=fake_logger)

    out_all_actions = mocked_kafka.get_values()
    assert config.kafka_produce in out_all_actions

    raw_data = out_all_actions[config.kafka_produce]
    messages: List[Message] = [Message.decode(x) for x in raw_data]
    assert ([x.dict(exclude=EXCLUDED_KEYS) for x in messages]
            == [x.dict(exclude=EXCLUDED_KEYS) for x in OUT_EXPECTED])
