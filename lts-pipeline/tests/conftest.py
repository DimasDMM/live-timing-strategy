from pytest_mock import MockerFixture
from typing import Callable, Dict, List, Optional

from ltspipe.messages import Message
from ltspipe.steps.listeners import WebsocketListenerStep
from tests.fixtures import *  # noqa: F401, F403
from tests.mocks.kafka import MockKafkaConsumer, MockKafkaProducer
from tests.mocks.requests import (
    MapRequests,
    MapRequestItem,
)
from tests.mocks.websocket import MockWebSocketApp

import warnings
warnings.filterwarnings('error')


def mock_multiprocessing_dict(
        mocker: MockerFixture,
        initial_dicts: List[dict]) -> List[dict]:
    """Mock dict in shared-memory."""
    mocker.patch(
        'multiprocessing.managers.SyncManager.dict',
        side_effect=initial_dicts)
    return initial_dicts


def mock_kafka_consumer_builder(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[Message]]) -> Dict[str, MockKafkaConsumer]:
    """Mock builders of Kafka consumer."""
    mocked_consumers = {topic: MockKafkaConsumer(messages=messages)
                        for topic, messages in kafka_topics.items()}
    mocker.patch(
        'ltspipe.steps.kafka.KafkaConsumerStep._build_kafka_consumer',
        new=lambda *args, **kwargs: _build_mock_kafka_consumer(
            mocked_consumers, *args, **kwargs))
    return mocked_consumers


def mock_kafka_producer_builder(
        mocker: MockerFixture,
        kafka_topics: Dict[str, List[Message]]) -> MockKafkaProducer:
    """Mock builders of Kafka producer."""
    mocked_kafka = MockKafkaProducer(messages_topic=kafka_topics)
    mocker.patch(
        'ltspipe.steps.kafka.KafkaProducerStep._build_kafka_producer',
        return_value=mocked_kafka)
    return mocked_kafka


def mock_requests(
        mocker: MockerFixture,
        requests_map: List[MapRequestItem]) -> MapRequests:
    """Mock get method of requests library."""
    mapper = MapRequests(requests_map=requests_map)
    mocker.patch(
        'requests.get',
        new=lambda url, *args, **kwargs: mapper.get(url))  # noqa: U100
    mocker.patch(
        'requests.delete',
        new=lambda url, *args, **kwargs: mapper.delete(url))  # noqa: U100
    mocker.patch(
        'requests.put',
        new=lambda url, *args, **kwargs: mapper.put(url))  # noqa: U100
    mocker.patch(
        'requests.post',
        new=lambda url, *args, **kwargs: mapper.post(url))  # noqa: U100
    return mapper


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


def _build_mock_kafka_consumer(
    mocked_consumers: Dict[str, MockKafkaConsumer],
    self: MockKafkaConsumer,  # noqa: U100
    topics: List[str],
    bootstrap_servers: List[str],  # noqa: U100
    group_id: Optional[str],  # noqa: U100
    value_deserializer: Callable,  # noqa: U100
) -> Optional[MockKafkaConsumer]:
    if topics[0] in mocked_consumers:
        return mocked_consumers[topics[0]]
    else:
        return None


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
