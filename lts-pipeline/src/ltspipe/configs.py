from dataclasses import dataclass, field
from typing import List

from ltspipe.data.enum import EnumBase
from ltspipe.messages import MessageSource


DEFAULT_API_SENDER_GROUP = 'api-sender'
DEFAULT_API_SENDER_ERRORS_PATH = 'artifacts/api/errors/'
DEFAULT_NOTIFICATIONS_TOPIC = 'notifications'
DEFAULT_PARSER_ERRORS_PATH = 'artifacts/parser/errors/'
DEFAULT_PARSER_GROUP = 'messages-parser'
DEFAULT_PARSER_UNKNOWNS_PATH = 'artifacts/parser/unknowns/'
DEFAULT_RAW_DATA_PATH = 'artifacts/raw/data/'
DEFAULT_RAW_ERRORS_PATH = 'artifacts/raw/errors/'
DEFAULT_RAW_MESSAGES_TOPIC = 'raw-messages'
DEFAULT_RAW_STORAGE_GROUP = 'raw-storage'
DEFAULT_STD_MESSAGES_TOPIC = 'standard'
DEFAULT_TEST_GROUP = 'test-group'
DEFAULT_TEST_TOPIC = 'test-topic'
DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_WS_ERRORS_PATH = 'artifacts/websocket/errors/'


class KafkaMode(EnumBase):
    """Enumeration of Kafka modes."""

    MODE_CONSUMER = 'kafka-consumer'
    MODE_PRODUCER = 'kafka-producer'


@dataclass(frozen=True)
class ApiSenderConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_API_SENDER_ERRORS_PATH)
    kafka_consume: str = field(default=DEFAULT_STD_MESSAGES_TOPIC)
    kafka_group: str = field(default=DEFAULT_API_SENDER_GROUP)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class KafkaCheckConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    test_mode: KafkaMode
    kafka_group: str = field(default=DEFAULT_TEST_GROUP)
    kafka_topic: str = field(default=DEFAULT_TEST_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class ManualListenerConfig:
    """Class to store the settings of the CLI script."""

    competition_code: str
    message_source: MessageSource
    kafka_servers: List[str]
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    kafka_produce: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class ParserConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_PARSER_ERRORS_PATH)
    kafka_consume: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    kafka_group: str = field(default=DEFAULT_PARSER_GROUP)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    kafka_produce: str = field(default=DEFAULT_STD_MESSAGES_TOPIC)
    unknowns_path: str = field(default=DEFAULT_PARSER_UNKNOWNS_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class RawStorageConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_RAW_ERRORS_PATH)
    kafka_group: str = field(default=DEFAULT_RAW_STORAGE_GROUP)
    kafka_consume: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsListenerConfig:
    """Class to store the settings of the CLI script."""

    competition_code: str
    kafka_servers: List[str]
    websocket_uri: str
    errors_path: str = field(default=DEFAULT_WS_ERRORS_PATH)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    kafka_produce: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)
