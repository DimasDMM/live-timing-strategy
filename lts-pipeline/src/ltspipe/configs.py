from dataclasses import dataclass, field
from typing import List

from ltspipe.data.enum import EnumBase
from ltspipe.messages import MessageSource


DEFAULT_NOTIFICATIONS_TOPIC = 'notifications'
DEFAULT_NOTIFICATIONS_LISTENER_GROUP = 'notifications-listener'
DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH = 'artifacts/notifications-listener/errors/'  # noqa
DEFAULT_RAW_DATA_PATH = 'artifacts/raw/data/'
DEFAULT_RAW_ERRORS_PATH = 'artifacts/raw/errors/'
DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_WS_PARSER_ERRORS_PATH = 'artifacts/ws-parser/errors/'
DEFAULT_WS_PARSER_UNKNOWNS_PATH = 'artifacts/ws-parser/unknowns/'


class KafkaMode(EnumBase):
    """Enumeration of Kafka modes."""

    MODE_CONSUMER = 'kafka-consumer'
    MODE_PRODUCER = 'kafka-producer'


@dataclass(frozen=True)
class KafkaCheckConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    test_mode: KafkaMode
    kafka_topic: str
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class ManualListenerConfig:
    """Class to store the settings of the CLI script."""

    competition_code: str
    message_source: MessageSource
    is_json: bool
    kafka_servers: List[str]
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    kafka_produce: str = field(default='')  # TODO: Remove this config
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class NotificationsListenerConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH)
    kafka_group: str = field(default=DEFAULT_NOTIFICATIONS_LISTENER_GROUP)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class RawStorageConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_RAW_ERRORS_PATH)
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsParserConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    competition_code: str
    kafka_servers: List[str]
    websocket_uri: str
    errors_path: str = field(default=DEFAULT_WS_PARSER_ERRORS_PATH)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    unknowns_path: str = field(default=DEFAULT_WS_PARSER_UNKNOWNS_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)
