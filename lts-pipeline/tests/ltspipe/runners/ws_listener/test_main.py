from datetime import datetime
from pytest_mock import MockerFixture
from typing import List

from ltspipe.configs import WsListenerConfig
from ltspipe.messages import Message, MessageSource
from ltspipe.runners.ws_listener.main import main
from tests.conftest import (
    mock_kafka_producer_builder,
    mock_websocket_builder,
)
from tests.helpers import load_raw_message
from tests.mocks.logging import FakeLogger


COMPETITION_CODE = 'test-competition'
EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}
KAFKA_SERVERS = ['localhost:9092']
WEBSOCKET_URI = 'ws://localhost:8000/ws/'

IN_WEBSOCKET = [
    load_raw_message('initial_3_teams.txt'),
    load_raw_message('initial_3_teams_with_times.txt'),
]
OUT_EXPECTED = [
    Message(
        competition_code=COMPETITION_CODE,
        data=load_raw_message('initial_3_teams.txt').strip(),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
        error_description=None,
        error_traceback=None,
    ),
    Message(
        competition_code=COMPETITION_CODE,
        data=load_raw_message('initial_3_teams_with_times.txt').strip(),
        source=MessageSource.SOURCE_WS_LISTENER,
        created_at=datetime.utcnow().timestamp(),
        updated_at=datetime.utcnow().timestamp(),
        error_description=None,
        error_traceback=None,
    ),
]


def test_main(mocker: MockerFixture) -> None:
    """Test main method."""
    mocked_kafka = mock_kafka_producer_builder(mocker)
    _ = mock_websocket_builder(mocker, messages=IN_WEBSOCKET)
    fake_logger = FakeLogger()
    config = WsListenerConfig(
        competition_code=COMPETITION_CODE,
        kafka_servers=KAFKA_SERVERS,
        websocket_uri=WEBSOCKET_URI,
    )

    main(config=config, logger=fake_logger)

    out_all_actions = mocked_kafka.get_values()
    assert config.kafka_produce in out_all_actions

    raw_data = out_all_actions[config.kafka_produce]
    messages: List[Message] = [Message.decode(x) for x in raw_data]
    assert ([x.dict(exclude=EXCLUDED_KEYS) for x in messages]
            == [x.dict(exclude=EXCLUDED_KEYS) for x in OUT_EXPECTED])
