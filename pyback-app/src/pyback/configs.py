from dataclasses import dataclass, field
from enum import Enum
from typing import Any, List


DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_RAW_DATA_PATH = 'artifacts/raw/'
DEFAULT_RAW_MESSAGES_TOPIC = 'raw-messages'
DEFAULT_RAW_STORAGE_GROUP = 'raw-storage'
DEFAULT_TEST_GROUP = 'test-group'
DEFAULT_TEST_TOPIC = 'test-topic'


class KafkaMode(Enum):
    """Enumeration of Kafka modes."""

    MODE_CONSUMER = 'kafka-consumer'
    MODE_PRODUCER = 'kafka-producer'

    def __eq__(self, other: Any) -> bool:
        """Compare enumeration to other objects and strings."""
        if self.__class__ is other.__class__:
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Build hash of current instance."""
        return hash(self.value)


@dataclass(frozen=True)
class RawStorageConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    kafka_topic: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    kafka_group: str = field(default=DEFAULT_RAW_STORAGE_GROUP)
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class KafkaCheckConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    test_mode: KafkaMode
    kafka_topic: str = field(default=DEFAULT_TEST_TOPIC)
    kafka_group: str = field(default=DEFAULT_TEST_GROUP)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsListenerConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    websocket_uri: str
    kafka_topic: str = field(default=DEFAULT_RAW_MESSAGES_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)
