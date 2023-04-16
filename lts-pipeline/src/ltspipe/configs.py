from dataclasses import dataclass, field
from typing import List

from ltspipe.data.enum import EnumBase


DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_RAW_DATA_PATH = 'artifacts/raw/'
DEFAULT_RAW_MESSAGES_TOPIC = 'raw-messages'
DEFAULT_RAW_STORAGE_GROUP = 'raw-storage'
DEFAULT_STD_MESSAGES_TOPIC = 'standard'
DEFAULT_PARSER_GROUP = 'messages-parser'
DEFAULT_PARSER_ERRORS_PATH = 'artifacts/parser/errors/'
DEFAULT_PARSER_UNKNOWNS_PATH = 'artifacts/parser/unknowns/'
DEFAULT_TEST_GROUP = 'test-group'
DEFAULT_TEST_TOPIC = 'test-topic'


class KafkaMode(EnumBase):
    """Enumeration of Kafka modes."""

    MODE_CONSUMER = 'kafka-consumer'
    MODE_PRODUCER = 'kafka-producer'


@dataclass(frozen=True)
class RawStorageConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    kafka_subscribe: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    kafka_group: str = field(default=DEFAULT_RAW_STORAGE_GROUP)
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class KafkaCheckConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    test_mode: KafkaMode
    kafka_subscribe: str = field(default=DEFAULT_TEST_TOPIC)
    kafka_group: str = field(default=DEFAULT_TEST_GROUP)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class ParserConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    kafka_subscribe: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    kafka_group: str = field(default=DEFAULT_PARSER_GROUP)
    kafka_produce: str = field(default=DEFAULT_STD_MESSAGES_TOPIC)
    errors_path: str = field(default=DEFAULT_PARSER_ERRORS_PATH)
    unknowns_path: str = field(default=DEFAULT_PARSER_UNKNOWNS_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsListenerConfig:
    """Class to store the settings of the CLI script."""

    competition_code: str
    kafka_servers: List[str]
    websocket_uri: str
    kafka_produce: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)
