from ltspipe.configs import (
    KafkaCheckConfig,
    KafkaMode,
    ParserConfig,
    RawStorageConfig,
    WsListenerConfig,
    DEFAULT_RAW_STORAGE_GROUP,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_STD_MESSAGES_TOPIC,
    DEFAULT_PARSER_ERRORS_PATH,
    DEFAULT_PARSER_UNKNOWNS_PATH,
    DEFAULT_TEST_GROUP,
    DEFAULT_TEST_TOPIC,
)


def test_raw_storage_config() -> None:
    """Test ltspipe.configs.RawStorageConfig."""
    kafka_servers = ['localhost:9092']
    raw_storage_config = RawStorageConfig(kafka_servers=kafka_servers)
    assert raw_storage_config.kafka_servers == kafka_servers
    assert raw_storage_config.kafka_subscribe == DEFAULT_RAW_MESSAGES_TOPIC
    assert raw_storage_config.kafka_group == DEFAULT_RAW_STORAGE_GROUP
    assert raw_storage_config.output_path == 'artifacts/raw/'
    assert raw_storage_config.verbosity == 2


def test_kafka_check_config() -> None:
    """Test ltspipe.configs.KafkaCheckConfig."""
    kafka_servers = ['localhost:9092']
    kafka_check_config = KafkaCheckConfig(
        kafka_servers=kafka_servers,
        test_mode=KafkaMode.MODE_PRODUCER,
    )
    assert kafka_check_config.kafka_servers == kafka_servers
    assert kafka_check_config.test_mode == KafkaMode.MODE_PRODUCER
    assert kafka_check_config.kafka_subscribe == DEFAULT_TEST_TOPIC
    assert kafka_check_config.kafka_group == DEFAULT_TEST_GROUP
    assert kafka_check_config.verbosity == 2


def test_parser_config() -> None:
    """Test ltspipe.configs.ParserConfig."""
    api_lts = 'http://localhost:8090/'
    kafka_servers = ['localhost:9092']
    parser_config = ParserConfig(
        api_lts=api_lts,
        kafka_servers=kafka_servers,
    )
    assert parser_config.kafka_servers == kafka_servers
    assert parser_config.kafka_subscribe == DEFAULT_RAW_MESSAGES_TOPIC
    assert parser_config.kafka_produce == DEFAULT_STD_MESSAGES_TOPIC
    assert parser_config.errors_path == DEFAULT_PARSER_ERRORS_PATH
    assert parser_config.unknowns_path == DEFAULT_PARSER_UNKNOWNS_PATH
    assert parser_config.verbosity == 2


def test_ws_listener_config() -> None:
    """Test ltspipe.configs.WsListenerConfig."""
    kafka_servers = ['localhost:9092']
    ws_listener_config = WsListenerConfig(
        competition_code='competition-sample-code',
        kafka_servers=kafka_servers,
        websocket_uri='ws://localhost:8000/ws/',
    )
    assert ws_listener_config.competition_code == 'competition-sample-code'
    assert ws_listener_config.kafka_servers == kafka_servers
    assert ws_listener_config.kafka_produce == DEFAULT_RAW_MESSAGES_TOPIC
    assert ws_listener_config.websocket_uri == 'ws://localhost:8000/ws/'
    assert ws_listener_config.verbosity == 2
