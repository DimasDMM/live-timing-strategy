import logging
import msgpack  # type: ignore
import os

from ltspipe.configs import RawStorageConfig
from ltspipe.steps.kafka import KafkaConsumerStep
from ltspipe.steps.filesystem import MessageStorageStep, RawStorageStep
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

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.debug(f'Topic consumer: {config.kafka_consume}')

    logger.info('Init processes...')
    raw_storage = RawStorageStep(
        logger=logger,
        output_path=config.output_path,
    )
    message_storage = MessageStorageStep(
        logger=logger,
        output_path=config.output_path,
        next_step=raw_storage,
    )
    errors_storage = MessageStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    kafka_consumer = KafkaConsumerStep(
        logger=logger,
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_consume],
        value_deserializer=msgpack.loads,
        group_id=config.kafka_group,
        next_step=message_storage,
        on_error=errors_storage,
    )
    logger.info('Processes created')

    logger.info('Start Kafka consumer...')
    kafka_consumer.start_step()
