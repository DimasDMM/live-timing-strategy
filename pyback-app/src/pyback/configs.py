from dataclasses import dataclass, field
from typing import List


DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_RAW_DATA_PATH = 'artifacts/raw/'


@dataclass(frozen=True)
class ListenerConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    listener_type: str
    listener_uri: str
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class RawStorageConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    output_path: str = field(default=DEFAULT_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class TestKafkaConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    test_mode: str
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsListenerConfig:
    """Class to store the settings of the CLI script."""

    kafka_servers: List[str]
    websocket_uri: str
    verbosity: int = field(default=DEFAULT_VERBOSITY)
