import logging
import msgpack  # type: ignore
import os

from ltspipe.configs import RawStorageConfig
from ltspipe.steps.kafka import KafkaConsumerStep
from ltspipe.steps.loggers import LogInfoStep
from ltspipe.steps.filesystem import FileStorageStep
from ltspipe.runners import BANNER_MSG


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

    logger.info(f'Create path if it does not exist: {config.output_path}')
    os.makedirs(config.output_path, exist_ok=True)

    logger.debug(f'Topic consumer: {config.kafka_consume}')

    logger.info('Init processes...')
    file_storage = FileStorageStep(
        logger=logger,
        output_path=config.output_path,
    )
    info_step = LogInfoStep(
        logger,
        next_step=file_storage,
    )
    kafka_consumer = KafkaConsumerStep(
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_consume],
        value_deserializer=msgpack.loads,
        next_step=info_step,
        group_id=config.kafka_group,
    )
    logger.info('Processes created')

    logger.info('Start Kafka consumer...')
    kafka_consumer.start_step()
