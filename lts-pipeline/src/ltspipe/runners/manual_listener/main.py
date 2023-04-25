from logging import Logger
import msgpack  # type: ignore
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
from time import sleep
from typing import Any, Callable, Dict, Iterable

from ltspipe.configs import ManualListenerConfig
from ltspipe.data.enum import FlagName
from ltspipe.data.notifications import NotificationType
from ltspipe.runners import BANNER_MSG, build_logger
from ltspipe.steps.bulk import (
    QueueDistributorStep,
    QueueForwardStep,
)
from ltspipe.steps.listeners import FileListenerStep
from ltspipe.steps.modifiers import FlagModifierStep
from ltspipe.steps.mappers import NotificationMapperStep
from ltspipe.steps.triggers import WsInitTriggerStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep


def main(config: ManualListenerConfig, logger: Logger) -> None:
    """
    Process to listen incoming data from a websocket.

    Params:
        config (ManualListenerConfig): configuration to run the method.
        logger (Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Competition code: {config.competition_code}')
    logger.debug(f'Topic producer: {config.kafka_produce}')

    with Manager() as manager:
        logger.info('Init shared-memory...')
        flags = manager.dict()
        queue = manager.dict()

        logger.info('Init processes...')
        p_not = _create_process(
            target=_run_notifications_listener,
            args=(config, flags, queue))  # type: ignore
        p_not.start()
        logger.info('Processes started')

        _run_input_listener(config, flags, queue)

        processes = {'notifications': p_not}
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
        config: ManualListenerConfig,
        flags: DictProxy,
        queue: DictProxy) -> None:
    """Run process with the notifications listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create notifications listener...')
    notification_listener = _build_notifications_process(
        config, logger, flags, queue)

    logger.info('Start notifications listener...')
    notification_listener.start_step()


def _run_input_listener(
        config: ManualListenerConfig,
        flags: DictProxy,
        queue: DictProxy) -> None:
    """Run process with the console input listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create input listener...')
    notification_listener = _build_file_listener_process(
        config, logger, flags, queue)

    logger.info('Start input listener...')
    notification_listener.start_step()


def _build_notifications_process(
        config: ManualListenerConfig,
        logger: Logger,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process with the notifications listener."""
    kafka_raw = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_produce,
        value_serializer=msgpack.dumps,
    )
    queue_forward = QueueForwardStep(
        logger=logger,
        queue=queue,  # type: ignore
        queue_step=kafka_raw,
    )
    flag_modifier = FlagModifierStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        flag_value=False,
        next_step=queue_forward,
    )
    mapper = NotificationMapperStep(
        logger=logger,
        map_notification={
            NotificationType.INIT_FINISHED: flag_modifier,
        },
    )
    kafka_consumer = KafkaConsumerStep(  # Without group ID
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_notifications],
        value_deserializer=msgpack.loads,
        next_step=mapper,
    )
    return kafka_consumer


def _build_file_listener_process(
        config: ManualListenerConfig,
        logger: Logger,
        flags: DictProxy,
        queue: DictProxy) -> FileListenerStep:
    """Build process with input listener."""
    kafka_raw = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_produce,
        value_serializer=msgpack.dumps,
    )
    kafka_notifications = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_notifications,
        value_serializer=msgpack.dumps,
    )
    flag_modifier = FlagModifierStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        flag_value=True,
        next_step=kafka_raw,
    )
    init_trigger = WsInitTriggerStep(
        logger=logger,
        on_init_trigger=kafka_notifications,
        on_init=flag_modifier,
        on_other=kafka_raw,
    )

    queue_distributor = QueueDistributorStep(
        logger=logger,
        flags=flags,  # type: ignore
        flag_name=FlagName.WAIT_INIT,
        queue=queue,  # type: ignore
        next_step=init_trigger,
    )
    ws_listener = FileListenerStep(
        logger,
        competition_code=config.competition_code,
        single_file=True,
        infinite_loop=True,
        message_source=config.message_source,
        next_step=queue_distributor,
    )

    return ws_listener
