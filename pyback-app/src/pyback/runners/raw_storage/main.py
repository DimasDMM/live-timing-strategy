import logging
import msgpack  # type: ignore

from pyback.configs import RawStorageConfig
from pyback.steps.kafka import KafkaConsumerStep
from pyback.steps.filesystem import FileStorageStep
from pyback.runners import BANNER_MSG


TOPIC_RAW_MESSAGES = 'raw-messages'
GROUP_RAW_STORAGE = 'raw-storage'


def main(
        config: RawStorageConfig,
        logger: logging.Logger) -> None:
    """
    Process to store raw messages.

    Params:
        config (RawStorageConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info('Init script...')
    file_storage = FileStorageStep(
        logger=logger,
        output_path=config.output_path,
    )
    kafka_consumer = KafkaConsumerStep(
        bootstrap_servers=config.kafka_servers,
        topics=[TOPIC_RAW_MESSAGES],
        value_deserializer=msgpack.loads,
        next_step=file_storage,
        group_id=GROUP_RAW_STORAGE,
    )

    logger.info('Start Kafka consumer...')
    kafka_consumer.start_step()
