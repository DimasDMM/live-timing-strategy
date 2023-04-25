from logging import Logger
import msgpack
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
import os
from time import sleep
from typing import Any, Callable, Dict, Iterable

from ltspipe.api.handlers import InitialDataHandler
from ltspipe.configs import ApiSenderConfig
from ltspipe.data.actions import ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import NotificationType
from ltspipe.steps.api import CompetitionInfoInitStep, ApiActionStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.mappers import NotificationMapperStep
from ltspipe.steps.triggers import ActionInitTriggerStep
from ltspipe.runners import BANNER_MSG, build_logger, do_auth


def main(config: ApiSenderConfig, logger: Logger) -> None:
    """
    Process to parse raw messages.

    Params:
        config (ApiSenderConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    auth_data = do_auth(api_url=config.api_lts.strip('/'))

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.debug(f'Topic consumer: {config.kafka_consume}')

    with Manager() as manager:
        logger.info('Init shared-memory...')
        competitions = manager.dict()

        logger.info('Init processes...')
        p_not = _create_process(
            target=_run_notifications_listener,
            args=(config, auth_data, competitions))  # type: ignore
        p_raw = _create_process(
            target=_run_std_listener,
            args=(config, auth_data, competitions))  # type: ignore
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
        config: ApiSenderConfig,
        auth_data: AuthData,
        competitions: DictProxy) -> None:
    """Run process with the notifications listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create notifications listener...')
    notification_listener = _build_notifications_process(
        config, logger, auth_data, competitions)

    logger.info('Start notifications listener...')
    notification_listener.start_step()


def _run_std_listener(
        config: ApiSenderConfig,
        auth_data: AuthData,
        competitions: DictProxy) -> None:
    """Run process with the parsers."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create parsers...')
    std_consumer = _build_std_process(
        config, logger, auth_data, competitions)

    logger.info('Start parsers...')
    std_consumer.start_step()


def _build_std_process(
        config: ApiSenderConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> KafkaConsumerStep:
    """Build process that consumes the standard data."""
    kafka_notifications = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_notifications,
        value_serializer=msgpack.dumps,
    )
    init_trigger = ActionInitTriggerStep(
        logger=logger,
        on_init_trigger=kafka_notifications,
    )
    api_actions = ApiActionStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
        competitions=competitions,  # type: ignore
        action_handlers={
            ActionType.INITIALIZE: InitialDataHandler(
                api_url=config.api_lts.strip('/'),
                auth_data=auth_data,
                competitions=competitions,  # type: ignore
            ),
        },
        next_step=init_trigger,
    )
    info_init = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
        auth_data=auth_data,
        competitions=competitions,  # type: ignore
        force_update=False,
        next_step=api_actions,
    )
    kafka_consumer = KafkaConsumerStep(  # Without group ID
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_consume],
        value_deserializer=msgpack.loads,
        next_step=info_init,
    )
    return kafka_consumer


def _build_notifications_process(
        config: ApiSenderConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> KafkaConsumerStep:
    """Build process with notifications listener."""
    api_getter = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
        auth_data=auth_data,
        competitions=competitions,  # type: ignore
        next_step=None,
    )
    mapper = NotificationMapperStep(
        logger=logger,
        map_notification={
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
