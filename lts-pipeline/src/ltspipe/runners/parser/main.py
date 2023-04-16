import logging
import msgpack  # type: ignore
import os
from typing import List

from ltspipe.configs import ParserConfig
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket import WsInitParser
from ltspipe.steps.filesystem import FileStorageStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.loggers import LogInfoStep
from ltspipe.steps.wrappers import ParsersStep
from ltspipe.runners import BANNER_MSG


def main(
        config: ParserConfig,
        logger: logging.Logger) -> None:
    """
    Process to parse raw messages.

    Params:
        config (ParserConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.info(f'Create path if it does not exist: {config.unknowns_path}')
    os.makedirs(config.unknowns_path, exist_ok=True)

    logger.info('Init parsers...')
    parsers: List[Parser] = [
        WsInitParser(),
    ]

    logger.info('Init pipeline steps...')
    errors_storage = FileStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    unknowns_storage = FileStorageStep(
        logger=logger,
        output_path=config.unknowns_path,
    )
    kafka_producer = KafkaProducerStep(
        logger=logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_produce,
        value_serializer=msgpack.dumps,
    )
    parser_step = ParsersStep(
        logger=logger,
        parsers=parsers,
        on_parsed=kafka_producer,
        on_error=errors_storage,
        on_unknown=unknowns_storage,
    )
    info_step = LogInfoStep(
        logger,
        next_step=parser_step,
    )
    kafka_consumer = KafkaConsumerStep(
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_subscribe],
        value_deserializer=msgpack.loads,
        next_step=info_step,
        group_id=config.kafka_group,
    )

    logger.info('Start Kafka consumer...')
    kafka_consumer.start_step()
