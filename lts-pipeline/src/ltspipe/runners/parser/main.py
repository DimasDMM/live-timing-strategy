from logging import Logger
import msgpack  # type: ignore
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
import os
from time import sleep
from typing import Any, Callable, Dict, Iterable, List

from ltspipe.configs import ParserConfig
from ltspipe.data.auth import AuthData
from ltspipe.data.enum import FlagName
from ltspipe.data.notifications import NotificationType
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.initial import InitialDataParser
from ltspipe.parsers.websocket.names import DriverNameParser, TeamNameParser
from ltspipe.runners import BANNER_MSG, build_logger, do_auth
from ltspipe.steps.api import CompetitionInfoInitStep
from ltspipe.steps.bulk import QueueDistributorStep, QueueForwardStep
from ltspipe.steps.filesystem import MessageStorageStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.mappers import NotificationMapperStep, WsParsersStep
from ltspipe.steps.modifiers import FlagModifierStep
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

    auth_data = do_auth(api_url=config.api_lts.strip('/'))

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.info(f'Create path if it does not exist: {config.unknowns_path}')
    os.makedirs(config.unknowns_path, exist_ok=True)

    logger.debug(f'Topic producer: {config.kafka_produce}')
    logger.debug(f'Topic consumer: {config.kafka_consume}')

    with Manager() as manager:
        logger.info('Init shared-memory...')
        competitions = manager.dict()
        flags = manager.dict()
        queue = manager.dict()

        logger.info('Init processes...')
        p_not = _create_process(
            target=_run_notifications_listener,
            args=(config, auth_data, competitions, flags, queue))
        p_raw = _create_process(
            target=_run_raw_listener,
            args=(config, auth_data, competitions, flags, queue))
        logger.info('Processes created')

        p_not.start()
        p_raw.start()
        logger.info('Processes started')

        processes = {'notifications': p_not, 'raw': p_raw}
        _join_processes(logger, processes)


def _create_process(target: Callable, args: Iterable[Any]) -> Process:
    """Create a parallel process."""
    return Process(
        target=target,
        args=args)  # type: ignore


def _join_processes(logger: Logger, processes: Dict[str, Process]) -> None:
    """Monitor processes and kill them if one of them dies."""
    process_died = False
    process_finished = False
    while not process_finished:
        for p_name, p in processes.items():
            if not p.is_alive():
                process_finished = True
                if p.exitcode != 0:
                    logger.warning(f'A process has died: {p_name}')
                    process_died = True
        if not process_finished:
            sleep(5)

    for p_name, p in processes.items():
        logger.warning(f'Kill process: {p_name}')
        p.kill()

    for _, p in processes.items():
        p.join()

    if process_died:
        exit(1)


def _run_notifications_listener(
        config: ParserConfig,
        auth_data: AuthData,
        competitions: DictProxy,
        flags: DictProxy,
        queue: DictProxy) -> None:
    """Run process with the notifications listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create input listener...')
    notification_listener = _build_notifications_process(
        config, logger, auth_data, competitions, flags, queue)

    logger.info('Start input listener...')
    notification_listener.start_step()


def _run_raw_listener(
        config: ParserConfig,
        auth_data: AuthData,
        competitions: DictProxy,
        flags: DictProxy,
        queue: DictProxy) -> None:
    """Run process with the raw data listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create raw listener...')
    rawe_listener = _build_raw_process(
        config, logger, auth_data, competitions, flags, queue)

    logger.info('Start raw listener...')
    rawe_listener.start_step()


def _build_raw_process(
        config: ParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process that consumes the raw data."""
    parsers_pipe = _build_parsers_pipe(config, logger, competitions)

    api_getter = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts,
        auth_data=auth_data,
        competitions=competitions,  # type: ignore
        next_step=parsers_pipe,
    )
    queue_distributor = QueueDistributorStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        queue=queue,  # type: ignore
        next_step=api_getter,
    )
    init_trigger = WsInitTriggerStep(
        logger=logger,
        on_init_trigger=None,
        on_init=parsers_pipe,
        on_other=queue_distributor,
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
        next_step=init_trigger,
        on_error=errors_storage,
    )
    return kafka_consumer


def _build_notifications_process(
        config: ParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process with notifications listener."""
    parsers_pipe = _build_parsers_pipe(config, logger, competitions)

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
        auth_data=auth_data,
        competitions=competitions,  # type: ignore
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
    errors_storage = MessageStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    kafka_consumer = KafkaConsumerStep(  # Without group ID
        logger=logger,
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_notifications],
        value_deserializer=msgpack.loads,
        next_step=mapper,
        on_error=errors_storage,
    )
    return kafka_consumer


def _build_parsers_pipe(
        config: ParserConfig,
        logger: Logger,
        competitions: DictProxy) -> WsParsersStep:  # noqa
    """Build pipe with data parsers."""
    initial_parser = InitialDataParser()
    parsers: List[Parser] = [
        DriverNameParser(competitions),  # type: ignore
        TeamNameParser(competitions),  # type: ignore
    ]

    kafka_producer = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_produce,
        value_serializer=msgpack.dumps,
    )
    unknowns_storage = MessageStorageStep(
        logger=logger,
        output_path=config.unknowns_path,
    )
    parser_step = WsParsersStep(
        logger=logger,
        initial_parser=initial_parser,
        parsers=parsers,
        on_parsed=kafka_producer,
        on_unknown=unknowns_storage,
    )
    return parser_step
