from datetime import datetime
import pytest
from pytest_mock import MockerFixture
from typing import Any, Dict, List

from ltspipe.configs import (
    WsListenerConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_RAW_MESSAGES_TOPIC,
)
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.enum import FlagName
from ltspipe.messages import Message, MessageDecoder, MessageSource
from ltspipe.runners.ws_listener.main import main
from tests.conftest import (
    mock_kafka_consumer_builder,
    mock_kafka_producer_builder,
    mock_multiprocessing_dict,
    mock_websocket_builder,
)
from tests.fixtures import MOCK_KAFKA, MOCK_WS, TEST_COMPETITION_CODE
from tests.helpers import load_raw_message
from tests.mocks.logging import FakeLogger
from tests.mocks.multiprocessing import MockProcess

EXCLUDED_KEYS = {
    'created_at': True,
    'updated_at': True,
}


def _mock_multiprocessing_process(mocker: MockerFixture) -> None:
    """Mock parallel processes by sequential ones."""
    mocker.patch(
        'ltspipe.runners.ws_listener.main._create_process',
        new=MockProcess)


@pytest.mark.parametrize(
    ('kafka_topics, in_websocket, in_queue, '
     'expected_kafka, expected_queue, expected_flags'),
    [
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [],
            },
            [  # in_websocket
                load_raw_message('init_qualy_with_times.txt'),
                load_raw_message('endurance_display_driver_name.txt'),
            ],
            {},  # in_queue
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.INIT_ONGOING,
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        decoder=MessageDecoder.NOTIFICATION,
                    ).encode(),
                ],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'init_qualy_with_times.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ).encode(),
                ],
            },
            {  # expected_queue
                TEST_COMPETITION_CODE: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=None,
                        error_traceback=None,
                    ),
                ],
            },
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: True},
            },
        ),
        (
            {  # kafka_topics
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.INIT_FINISHED,
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        decoder=MessageDecoder.NOTIFICATION,
                    ).encode(),
                ],
            },
            [],  # in_websocket
            {  # in_queue
                TEST_COMPETITION_CODE: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ),
                ],
            },
            {  # expected_kafka
                DEFAULT_NOTIFICATIONS_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=Notification(
                            type=NotificationType.INIT_FINISHED,
                        ),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        decoder=MessageDecoder.NOTIFICATION,
                    ).encode(),
                ],
                DEFAULT_RAW_MESSAGES_TOPIC: [
                    Message(
                        competition_code=TEST_COMPETITION_CODE,
                        data=load_raw_message(
                            'endurance_display_driver_name.txt').strip(),
                        source=MessageSource.SOURCE_WS_LISTENER,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                    ).encode(),
                ],
            },
            {TEST_COMPETITION_CODE: []},  # expected_queue
            {  # expected_flags
                TEST_COMPETITION_CODE: {FlagName.WAIT_INIT: False},
            },
        ),
    ],
)
def test_main(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[str]],
        in_websocket: List[str],
        in_queue: Dict[str, List[Message]],
        expected_kafka: Dict[str, List[str]],
        expected_queue: Dict[str, List[Message]],
        expected_flags: dict) -> None:
    """Test main method."""
    config = WsListenerConfig(
        competition_code=TEST_COMPETITION_CODE,
        kafka_servers=MOCK_KAFKA,
        websocket_uri=MOCK_WS,
    )

    in_flags: Dict[str, Dict[FlagName, Any]] = {}
    _mock_multiprocessing_process(mocker)
    mock_multiprocessing_dict(mocker, initial_dicts=[in_flags, in_queue])
    mock_kafka_consumer_builder(mocker, kafka_topics=kafka_topics)
    mock_kafka_producer_builder(mocker, kafka_topics=kafka_topics)
    mock_websocket_builder(mocker, messages=in_websocket)
    fake_logger = FakeLogger()

    main(config=config, logger=fake_logger)

    # Validate that the value of the flag is the expected one
    assert in_flags == expected_flags

    # Validate that the messages are received by Kafka
    out_kafka = {topic: _raw_to_dict(raw)
                 for topic, raw in kafka_topics.items()}
    assert (out_kafka == {topic: _raw_to_dict(raw)
                          for topic, raw in expected_kafka.items()})

    # Validate that the expected messages are in the queue
    assert ({code: _msg_to_dict(x) for code, x in in_queue.items()}
            == {code: _msg_to_dict(x) for code, x in expected_queue.items()})


def _raw_to_dict(raw: List[str]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [Message.decode(x).dict(exclude=EXCLUDED_KEYS) for x in raw]


def _msg_to_dict(raw: List[Message]) -> List[dict]:
    """Transform messages into dictionaries."""
    return [x.model_dump(exclude=EXCLUDED_KEYS) for x in raw]
