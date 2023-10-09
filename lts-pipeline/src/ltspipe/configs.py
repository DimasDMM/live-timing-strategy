from dataclasses import dataclass, field
from typing import List, Optional


DEFAULT_NOTIFICATIONS_TOPIC = 'notifications'
DEFAULT_NOTIFICATIONS_LISTENER_GROUP = 'notifications-listener'
DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH = 'artifacts/notifications-listener/errors/'  # noqa
DEFAULT_VERBOSITY = 2  # 0: Disabled, 1: Debug, 2: Info, ...
DEFAULT_WS_PARSER_ERRORS_PATH = 'artifacts/ws-parser/errors/'
DEFAULT_WS_PARSER_UNKNOWNS_PATH = 'artifacts/ws-parser/unknowns/'
DEFAULT_WS_RAW_DATA_PATH = 'artifacts/ws-raw/data/'
DEFAULT_WS_RAW_ERRORS_PATH = 'artifacts/ws-raw/errors/'


@dataclass(frozen=True)
class NotificationsListenerConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    competition_code: str
    kafka_servers: List[str]
    errors_path: str = field(default=DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH)
    kafka_group: str = field(default=DEFAULT_NOTIFICATIONS_LISTENER_GROUP)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    verbosity: int = field(default=DEFAULT_VERBOSITY)


@dataclass(frozen=True)
class WsParserConfig:
    """Class to store the settings of the CLI script."""

    api_lts: str
    competition_code: str
    kafka_servers: List[str]
    websocket_uri: Optional[str] = field(default=None)
    websocket_path: Optional[str] = field(default=None)
    errors_path: str = field(default=DEFAULT_WS_PARSER_ERRORS_PATH)
    kafka_notifications: str = field(default=DEFAULT_NOTIFICATIONS_TOPIC)
    unknowns_path: str = field(default=DEFAULT_WS_PARSER_UNKNOWNS_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)

    def __post_init__(self) -> None:
        """Validate content."""
        if self.websocket_uri is None and self.websocket_path is None:
            raise Exception('Both websocket URI and path are empty.')
        elif self.websocket_uri is not None and self.websocket_path is not None:
            raise Exception('Cannot use websocket URI and path together.')


@dataclass(frozen=True)
class WsRawStorageConfig:
    """Class to store the settings of the CLI script."""

    competition_code: str
    kafka_servers: List[str]
    websocket_uri: str
    errors_path: str = field(default=DEFAULT_WS_RAW_ERRORS_PATH)
    output_path: str = field(default=DEFAULT_WS_RAW_DATA_PATH)
    verbosity: int = field(default=DEFAULT_VERBOSITY)
