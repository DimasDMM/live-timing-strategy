from logging import Logger
import msgpack
from multiprocessing import Process
import os
from time import sleep
from typing import Any, Callable, Dict, Iterable

from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.handlers.strategy import (
    StrategyPitsStatsHandler,
)
from ltspipe.configs import NotificationsListenerConfig
from ltspipe.data.actions import ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.data.notifications import NotificationType
from ltspipe.parsers.strategy import StrategyPitsStatsParser
from ltspipe.steps.api import ApiActionStep, CompetitionInfoRefreshStep
from ltspipe.steps.filesystem import MessageStorageStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.mappers import NotificationMapperStep
from ltspipe.steps.strategy import StrategyStep
from ltspipe.runners import BANNER_MSG, build_logger, do_auth


def main(config: NotificationsListenerConfig, logger: Logger) -> None:
    """
    Process to parse raw messages.

    Params:
        config (NotificationsListenerConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    auth_data = do_auth(api_url=config.api_lts.strip('/'))

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.debug(f'Topic notifications: {config.kafka_notifications}')

    info = build_competition_info(
        config.api_lts,
        bearer=auth_data.bearer,
        competition_code=config.competition_code)
    if info is None:
        raise Exception(
            f'Competition does not exist: {config.competition_code}')

    logger.info('Init processes...')
    p_not = _create_process(
        target=_run_notifications_listener,
        args=(config, auth_data, info))  # type: ignore
    logger.info('Processes created')

    p_not.start()
    logger.info('Processes started')

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
        config: NotificationsListenerConfig,
        auth_data: AuthData,
        info: CompetitionInfo) -> None:
    """Run process with the notifications listener."""
    logger = build_logger(__package__, config.verbosity)
    logger.info('Create notifications listener...')
    notification_listener = _build_notifications_process(
        config, logger, auth_data, info)

    logger.info('Start notifications listener...')
    notification_listener.start_step()


def _build_notifications_process(
        config: NotificationsListenerConfig,
        logger: Logger,
        auth_data: AuthData,
        info: CompetitionInfo) -> KafkaConsumerStep:
    """Build process with notifications listener."""
    mapper = _build_notifications_mapper_step(
        config, logger, auth_data, info)

    errors_storage = MessageStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    kafka_consumer = KafkaConsumerStep(  # Without group ID
        logger=logger,
        info=info,
        bootstrap_servers=config.kafka_servers,
        topics=[config.kafka_notifications],
        value_deserializer=msgpack.loads,
        next_step=mapper,
        on_error=errors_storage,
    )
    return kafka_consumer


def _build_notifications_mapper_step(
        config: NotificationsListenerConfig,
        logger: Logger,
        auth_data: AuthData,
        info: CompetitionInfo) -> NotificationMapperStep:
    """Build notifications mapper step."""
    kafka_notifications = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_notifications,
        value_serializer=msgpack.dumps,
    )
    api_step = ApiActionStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
        info=info,
        action_handlers=_build_action_handlers(config, auth_data, info),
        notification_step=kafka_notifications,
        next_step=None,
    )

    mapper = NotificationMapperStep(
        logger=logger,
        map_notification={
            NotificationType.ADDED_PIT_IN: StrategyStep(
                logger=logger,
                parser=StrategyPitsStatsParser(
                    api_url=config.api_lts,
                    auth_data=auth_data,
                    info=info,
                ),
                on_parsed=api_step,
                on_unknown=None,
            ),
            NotificationType.REFRESH_INFO: CompetitionInfoRefreshStep(
                logger=logger,
                api_lts=config.api_lts,
                auth_data=auth_data,
                info=info,
            ),
        },
    )

    return mapper


def _build_action_handlers(
        config: NotificationsListenerConfig,
        auth_data: AuthData,
        info: CompetitionInfo) -> Dict[ActionType, ApiHandler]:
    """Build map of handlers applied to action types."""
    return {
        ActionType.ADD_STRATEGY_PITS_STATS: StrategyPitsStatsHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            info=info,
        ),
    }
