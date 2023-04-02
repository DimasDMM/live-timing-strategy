from pyback.configs import (
    KafkaCheckConfig,
    KafkaMode,
    RawStorageConfig,
    WsListenerConfig,
    DEFAULT_RAW_STORAGE_GROUP,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_TEST_GROUP,
    DEFAULT_TEST_TOPIC,
)


def test_raw_storage_config() -> None:
    """Test pyback.configs.RawStorageConfig."""
    kafka_servers = ['localhost:9092']
    raw_storage_config = RawStorageConfig(kafka_servers=kafka_servers)
    assert raw_storage_config.kafka_servers == kafka_servers
    assert raw_storage_config.kafka_topic == DEFAULT_RAW_MESSAGES_TOPIC
    assert raw_storage_config.kafka_group == DEFAULT_RAW_STORAGE_GROUP
    assert raw_storage_config.output_path == 'artifacts/raw/'
    assert raw_storage_config.verbosity == 2


def test_kafka_check_config() -> None:
    """Test pyback.configs.KafkaCheckConfig."""
    kafka_servers = ['localhost:9092']
    kafka_check_config = KafkaCheckConfig(
        kafka_servers=kafka_servers,
        test_mode=KafkaMode.MODE_PRODUCER,
    )
    assert kafka_check_config.kafka_servers == kafka_servers
    assert kafka_check_config.test_mode == KafkaMode.MODE_PRODUCER
    assert kafka_check_config.kafka_topic == DEFAULT_TEST_TOPIC
    assert kafka_check_config.kafka_group == DEFAULT_TEST_GROUP
    assert kafka_check_config.verbosity == 2


def test_ws_listener_config() -> None:
    """Test pyback.configs.WsListenerConfig."""
    kafka_servers = ['localhost:9092']
    ws_listener_config = WsListenerConfig(
        competition_code='competition-sample-code',
        kafka_servers=kafka_servers,
        websocket_uri='ws://localhost:8000/ws/',
    )
    assert ws_listener_config.competition_code == 'competition-sample-code'
    assert ws_listener_config.kafka_servers == kafka_servers
    assert ws_listener_config.kafka_topic == DEFAULT_RAW_MESSAGES_TOPIC
    assert ws_listener_config.websocket_uri == 'ws://localhost:8000/ws/'
    assert ws_listener_config.verbosity == 2
