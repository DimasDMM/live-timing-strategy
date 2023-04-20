from logging import Logger
import msgpack  # type: ignore
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
import os
from typing import List

from ltspipe.configs import ParserConfig
from ltspipe.data.enum import FlagName
from ltspipe.data.notifications import NotificationType
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket import WsInitParser
from ltspipe.runners import BANNER_MSG
from ltspipe.steps.api import CompetitionInfoInitStep
from ltspipe.steps.bulk import QueueDistributorStep, QueueForwardStep
from ltspipe.steps.filesystem import FileStorageStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.loggers import LogInfoStep
from ltspipe.steps.modifiers import FlagModifierStep
from ltspipe.steps.mappers import NotificationMapperStep, ParsersStep
from ltspipe.steps.triggers import WsInitTriggerStep


def main(config: ParserConfig, logger: Logger) -> None:
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

    logger.debug(f'Topic producer: {config.kafka_produce}')
    logger.debug(f'Topic consumer: {config.kafka_consume}')

    with Manager() as manager:
        logger.info('Init script...')
        flags = manager.dict()
        queue = manager.dict()
        raw_consumer = _build_raw_process(config, logger, flags, queue)
        notification_listener = _build_notifications_process(
            config, logger, flags, queue)

        logger.info('Start notifications listener...')
        p_not = Process(
            target=notification_listener.start_step())  # type: ignore
        p_not.start()

        logger.info('Start raw-data consumer...')
        p_raw = Process(target=raw_consumer.start_step())  # type: ignore
        p_raw.start()

        p_not.join()
        p_raw.join()


def _build_raw_process(
        config: ParserConfig,
        logger: Logger,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process that consumes the raw data."""
    parsers_pipe = _build_parsers_pipe(config=config, logger=logger)
    queue_distributor = QueueDistributorStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        queue=queue,  # type: ignore
        next_step=parsers_pipe,
    )
    init_trigger = WsInitTriggerStep(
        logger=logger,
        on_init_trigger=None,
        on_init=parsers_pipe,
        on_other=queue_distributor,
    )

    info_step = LogInfoStep(
        logger,
        next_step=init_trigger,
    )
    kafka_consumer = KafkaConsumerStep(
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_consume],
        value_deserializer=msgpack.loads,
        next_step=info_step,
        group_id=config.kafka_group,
    )
    return kafka_consumer


def _build_notifications_process(
        config: ParserConfig,
        logger: Logger,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process with notifications listener."""
    parsers_pipe = _build_parsers_pipe(config=config, logger=logger)

    queue_forward = QueueForwardStep(
        logger=logger,
        queue=queue,  # type: ignore
        queue_step=parsers_pipe,
    )

    flag_init_finished = FlagModifierStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        flag_value=False,
        next_step=queue_forward,
    )
    api_getter = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts,
        competitions={},
        next_step=flag_init_finished,
    )

    flag_init_ongoing = FlagModifierStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        flag_value=True,
        next_step=None,
    )

    mapper = NotificationMapperStep(
        logger=logger,
        map_notification={
            NotificationType.INIT_ONGOING: flag_init_ongoing,
            NotificationType.INIT_FINISHED: api_getter,
        },
    )
    kafka_consumer = KafkaConsumerStep(  # Without group ID
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_notifications],
        value_deserializer=msgpack.loads,
        next_step=mapper,
    )
    return kafka_consumer


def _build_parsers_pipe(config: ParserConfig, logger: Logger) -> ParsersStep:
    """Build pipe with data parsers."""
    parsers: List[Parser] = [
        WsInitParser(),
    ]

    kafka_producer = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_produce,
        value_serializer=msgpack.dumps,
    )
    errors_storage = FileStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    unknowns_storage = FileStorageStep(
        logger=logger,
        output_path=config.unknowns_path,
    )
    parser_step = ParsersStep(
        logger=logger,
        parsers=parsers,
        on_parsed=kafka_producer,
        on_error=errors_storage,
        on_unknown=unknowns_storage,
    )
    return parser_step
