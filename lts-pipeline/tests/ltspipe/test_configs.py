from ltspipe.configs import (
    ApiSenderConfig,
    KafkaCheckConfig,
    KafkaMode,
    NotificationsListenerConfig,
    ParserConfig,
    RawStorageConfig,
    WsListenerConfig,
    DEFAULT_API_SENDER_GROUP,
    DEFAULT_API_SENDER_ERRORS_PATH,
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH,
    DEFAULT_NOTIFICATIONS_LISTENER_GROUP,
    DEFAULT_PARSER_ERRORS_PATH,
    DEFAULT_PARSER_GROUP,
    DEFAULT_PARSER_UNKNOWNS_PATH,
    DEFAULT_RAW_DATA_PATH,
    DEFAULT_RAW_ERRORS_PATH,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_RAW_STORAGE_GROUP,
    DEFAULT_STD_MESSAGES_TOPIC,
    DEFAULT_TEST_GROUP,
    DEFAULT_TEST_TOPIC,
    DEFAULT_VERBOSITY,
    DEFAULT_WS_ERRORS_PATH,
)
from tests.fixtures import (
    MOCK_API_LTS,
    MOCK_KAFKA,
    MOCK_WS,
    TEST_COMPETITION_CODE,
)


def test_api_sender_config() -> None:
    """Test ltspipe.configs.ApiSenderConfig."""
    api_sender_config = ApiSenderConfig(
        api_lts=MOCK_API_LTS,
        kafka_servers=MOCK_KAFKA,
    )

    assert api_sender_config.api_lts == MOCK_API_LTS
    assert api_sender_config.errors_path == DEFAULT_API_SENDER_ERRORS_PATH
    assert api_sender_config.kafka_consume == DEFAULT_STD_MESSAGES_TOPIC
    assert api_sender_config.kafka_group == DEFAULT_API_SENDER_GROUP
    assert api_sender_config.kafka_notifications == DEFAULT_NOTIFICATIONS_TOPIC
    assert api_sender_config.kafka_servers == MOCK_KAFKA
    assert api_sender_config.verbosity == DEFAULT_VERBOSITY


def test_kafka_check_config() -> None:
    """Test ltspipe.configs.KafkaCheckConfig."""
    kafka_servers = ['localhost:9092']
    kafka_check_config = KafkaCheckConfig(
        kafka_servers=kafka_servers,
        test_mode=KafkaMode.MODE_PRODUCER,
    )
    assert kafka_check_config.kafka_servers == kafka_servers
    assert kafka_check_config.test_mode == KafkaMode.MODE_PRODUCER
    assert kafka_check_config.kafka_topic == DEFAULT_TEST_TOPIC
    assert kafka_check_config.kafka_group == DEFAULT_TEST_GROUP
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


def test_parser_config() -> None:
    """Test ltspipe.configs.ParserConfig."""
    parser_config = ParserConfig(
        api_lts=MOCK_API_LTS,
        kafka_servers=MOCK_KAFKA,
    )

    assert parser_config.api_lts == MOCK_API_LTS
    assert parser_config.errors_path == DEFAULT_PARSER_ERRORS_PATH
    assert parser_config.kafka_consume == DEFAULT_RAW_MESSAGES_TOPIC
    assert parser_config.kafka_group == DEFAULT_PARSER_GROUP
    assert parser_config.kafka_notifications == DEFAULT_NOTIFICATIONS_TOPIC
    assert parser_config.kafka_servers == MOCK_KAFKA
    assert parser_config.kafka_produce == DEFAULT_STD_MESSAGES_TOPIC
    assert parser_config.unknowns_path == DEFAULT_PARSER_UNKNOWNS_PATH
    assert parser_config.verbosity == DEFAULT_VERBOSITY


def test_raw_storage_config() -> None:
    """Test ltspipe.configs.RawStorageConfig."""
    kafka_servers = ['localhost:9092']
    raw_storage_config = RawStorageConfig(kafka_servers=kafka_servers)
    assert raw_storage_config.errors_path == DEFAULT_RAW_ERRORS_PATH
    assert raw_storage_config.kafka_servers == kafka_servers
    assert raw_storage_config.kafka_consume == DEFAULT_RAW_MESSAGES_TOPIC
    assert raw_storage_config.kafka_group == DEFAULT_RAW_STORAGE_GROUP
    assert raw_storage_config.output_path == DEFAULT_RAW_DATA_PATH
    assert raw_storage_config.verbosity == DEFAULT_VERBOSITY


def test_ws_listener_config() -> None:
    """Test ltspipe.configs.WsListenerConfig."""
    ws_listener_config = WsListenerConfig(
        competition_code=TEST_COMPETITION_CODE,
        kafka_servers=MOCK_KAFKA,
        websocket_uri=MOCK_WS,
    )
    assert ws_listener_config.competition_code == TEST_COMPETITION_CODE
    assert ws_listener_config.errors_path == DEFAULT_WS_ERRORS_PATH
    assert ws_listener_config.kafka_notifications == DEFAULT_NOTIFICATIONS_TOPIC
    assert ws_listener_config.kafka_servers == MOCK_KAFKA
    assert ws_listener_config.kafka_produce == DEFAULT_RAW_MESSAGES_TOPIC
    assert ws_listener_config.websocket_uri == MOCK_WS
    assert ws_listener_config.verbosity == DEFAULT_VERBOSITY
