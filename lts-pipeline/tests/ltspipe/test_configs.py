from ltspipe.configs import (
    KafkaCheckConfig,
    KafkaMode,
    NotificationsListenerConfig,
    RawStorageConfig,
    WsParserConfig,
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH,
    DEFAULT_NOTIFICATIONS_LISTENER_GROUP,
    DEFAULT_RAW_DATA_PATH,
    DEFAULT_RAW_ERRORS_PATH,
    DEFAULT_VERBOSITY,
)
from tests.fixtures import (
    MOCK_API_LTS,
    MOCK_KAFKA,
    MOCK_WS,
    TEST_COMPETITION_CODE,
)


def test_kafka_check_config() -> None:
    """Test ltspipe.configs.KafkaCheckConfig."""
    kafka_servers = ['localhost:9092']
    kafka_check_config = KafkaCheckConfig(
        kafka_servers=kafka_servers,
        kafka_topic='',
        test_mode=KafkaMode.MODE_PRODUCER,
    )
    assert kafka_check_config.kafka_servers == kafka_servers
    assert kafka_check_config.test_mode == KafkaMode.MODE_PRODUCER
    assert kafka_check_config.kafka_topic == ''
    assert kafka_check_config.verbosity == DEFAULT_VERBOSITY


def test_notifications_listener_config() -> None:
    """Test ltspipe.configs.ApiSenderConfig."""
    config = NotificationsListenerConfig(
        api_lts=MOCK_API_LTS,
        kafka_servers=MOCK_KAFKA,
    )

    assert config.api_lts == MOCK_API_LTS
    assert config.errors_path == DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH
    assert config.kafka_group == DEFAULT_NOTIFICATIONS_LISTENER_GROUP
    assert config.kafka_notifications == DEFAULT_NOTIFICATIONS_TOPIC
    assert config.kafka_servers == MOCK_KAFKA
    assert config.verbosity == DEFAULT_VERBOSITY


def test_raw_storage_config() -> None:
    """Test ltspipe.configs.RawStorageConfig."""
    kafka_servers = ['localhost:9092']
    raw_storage_config = RawStorageConfig(kafka_servers=kafka_servers)
    assert raw_storage_config.errors_path == DEFAULT_RAW_ERRORS_PATH
    assert raw_storage_config.kafka_servers == kafka_servers
    assert raw_storage_config.output_path == DEFAULT_RAW_DATA_PATH
    assert raw_storage_config.verbosity == DEFAULT_VERBOSITY


def test_ws_parser_config() -> None:
    """Test ltspipe.configs.WsParserConfig."""
    ws_parser_config = WsParserConfig(
        api_lts=MOCK_API_LTS,
        competition_code=TEST_COMPETITION_CODE,
        kafka_servers=MOCK_KAFKA,
        websocket_uri=MOCK_WS,
    )
    assert ws_parser_config.api_lts == MOCK_API_LTS
    assert ws_parser_config.competition_code == TEST_COMPETITION_CODE
    assert ws_parser_config.errors_path == DEFAULT_WS_ERRORS_PATH
    assert ws_parser_config.kafka_notifications == DEFAULT_NOTIFICATIONS_TOPIC
    assert ws_parser_config.kafka_servers == MOCK_KAFKA
    assert ws_parser_config.websocket_uri == MOCK_WS
    assert ws_parser_config.verbosity == DEFAULT_VERBOSITY
