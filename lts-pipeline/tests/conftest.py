from pytest_mock import MockerFixture
from typing import Callable, List

from ltspipe.messages import Message
from ltspipe.steps.listeners import WebsocketListenerStep
from tests.fixtures import *  # noqa: F401, F403
from tests.mocks.kafka import MockKafkaConsumer, MockKafkaProducer
from tests.mocks.websocket import MockWebSocketApp

import warnings
warnings.filterwarnings('error')


def mock_kafka_consumer_builder(
        mocker: MockerFixture,
        messages: List[Message]) -> MockKafkaConsumer:
    """Mock builders of Kafka consumer."""
    mocked_kafka = MockKafkaConsumer(messages)
    mocker.patch(
        'ltspipe.steps.kafka.KafkaConsumerStep._build_kafka_consumer',
        return_value=mocked_kafka)
    return mocked_kafka


def mock_kafka_producer_builder(mocker: MockerFixture) -> MockKafkaProducer:
    """Mock builders of Kafka producer."""
    mocked_kafka = MockKafkaProducer()
    mocker.patch(
        'ltspipe.steps.kafka.KafkaProducerStep._build_kafka_producer',
        return_value=mocked_kafka)
    return mocked_kafka


def mock_websocket_builder(
        mocker: MockerFixture,
        messages: List[str]) -> MockWebSocketApp:
    """Mock builders of websocket."""
    mocked_socket = MockWebSocketApp(messages=messages)
    mocker.patch(
        'ltspipe.steps.listeners.WebsocketListenerStep._build_websocket',
        new=lambda *args, **kwargs: _build_mock_websocket(
            mocked_socket, *args, **kwargs))
    return mocked_socket


def _build_mock_websocket(
        mocked_socket: MockWebSocketApp,
        self: WebsocketListenerStep,  # noqa: U100
        uri: str,  # noqa: U100
        on_message: Callable,
        on_error: Callable,
        on_close: Callable,
        on_open: Callable) -> MockWebSocketApp:
    mocked_socket.set_on_message(on_message)
    mocked_socket.set_on_error(on_error)
    mocked_socket.set_on_close(on_close)
    mocked_socket.set_on_open(on_open)
    return mocked_socket
