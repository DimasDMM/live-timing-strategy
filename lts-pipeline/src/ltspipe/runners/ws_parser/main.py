from logging import Logger
import msgpack  # type: ignore
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
import os
from time import sleep
from typing import Any, Callable, Dict, Iterable, List

from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.handlers.competitions_metadata import (
    UpdateCompetitionMetadataRemainingHandler,
    UpdateCompetitionMetadataStatusHandler,
)
from ltspipe.api.handlers.initial import InitialDataHandler
from ltspipe.api.handlers.participants import (
    UpdateDriverHandler,
    UpdateTeamHandler,
)
from ltspipe.api.handlers.pits import AddPitInHandler, AddPitOutHandler
from ltspipe.api.handlers.timing import (
    UpdateTimingBestTimeHandler,
    UpdateTimingLapHandler,
    UpdateTimingLastTimeHandler,
    UpdateTimingNumberPitsHandler,
    UpdateTimingPitTimeHandler,
    UpdateTimingPositionHandler,
)
from ltspipe.configs import WsParserConfig
from ltspipe.data.actions import ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import NotificationType
from ltspipe.messages import MessageSource
from ltspipe.parsers.base import Parser
from ltspipe.parsers.websocket.competitions_metadata import (
    CompetitionMetadataRemainingParser,
    CompetitionMetadataStatusParser,
)
from ltspipe.parsers.websocket.initial import InitialDataParser
from ltspipe.parsers.websocket.participants import (
    DriverNameParser,
    TeamNameParser,
)
from ltspipe.parsers.websocket.pits import PitInParser, PitOutParser
from ltspipe.parsers.websocket.timing import (
    TimingBestTimeParser,
    TimingLapParser,
    TimingLastTimeParser,
    TimingNumberPitsParser,
    TimingPitTimeParser,
    TimingPositionParser,
)
from ltspipe.runners import BANNER_MSG, build_logger, do_auth
from ltspipe.steps.api import CompetitionInfoRefreshStep, ApiActionStep
from ltspipe.steps.base import MidStep, StartStep
from ltspipe.steps.filesystem import MessageStorageStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.listeners import FileListenerStep, WebsocketListenerStep
from ltspipe.steps.mappers import NotificationMapperStep, WsParsersStep


def main(config: WsParserConfig, logger: Logger) -> None:
    """
    Process to parse raw websocket messages.

    Params:
        config (WsParserConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    auth_data = do_auth(api_url=config.api_lts.strip('/'))

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.info(f'Create path if it does not exist: {config.unknowns_path}')
    os.makedirs(config.unknowns_path, exist_ok=True)

    logger.debug(f'Topic notifications: {config.kafka_notifications}')
    logger.debug(f'Topic servers: {config.kafka_servers}')

    with Manager() as manager:
        logger.info('Init shared-memory...')
        competitions = manager.dict()

        info = build_competition_info(
            config.api_lts,
            bearer=auth_data.bearer,
            competition_code=config.competition_code)
        if info is None:
            raise Exception(
                f'Competition does not exist: {config.competition_code}')
        competitions[config.competition_code] = info

        logger.info('Init processes...')

        process_logger = build_logger(__package__, config.verbosity)
        p_not = _create_process(
            target=_run_notifications_listener,
            args=(config, process_logger, auth_data, competitions))
        p_ws = _create_process(
            target=_run_ws_listener,
            args=(config, process_logger, auth_data, competitions))
        logger.info('Processes created')

        p_not.start()
        p_ws.start()
        logger.info('Processes started')

        processes = {'notifications': p_not, 'ws': p_ws}
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
        config: WsParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> None:
    """Run process with the notifications listener."""
    logger.info('Create input listener...')
    notification_listener = _build_notifications_process(
        config, logger, auth_data, competitions)

    logger.info('Start input listener...')
    notification_listener.start_step()


def _run_ws_listener(
        config: WsParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> None:
    """Run process with the raw data listener."""
    logger.info('Create websocket listener...')
    ws_listener = _build_ws_process(
        config, logger, auth_data, competitions)

    logger.info('Start websocket listener...')
    ws_listener.start_step()


def _build_ws_process(
        config: WsParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> StartStep:
    """Build process that consumes the raw data."""
    kafka_notifications = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_notifications,
        value_serializer=msgpack.dumps,
    )
    api_actions = ApiActionStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
        competitions=competitions,  # type: ignore
        action_handlers=_build_action_handlers(config, auth_data, competitions),
        notification_step=kafka_notifications,
        next_step=None,
    )

    parsers_pipe = _build_parsers_pipe(
        config, logger, competitions, api_actions)

    errors_storage = MessageStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )

    ws_listener: StartStep
    if config.websocket_uri is not None:
        ws_listener = WebsocketListenerStep(
            logger,
            competition_code=config.competition_code,
            uri=config.websocket_uri,
            next_step=parsers_pipe,
            on_error=errors_storage,
        )
    elif config.websocket_path is not None:
        ws_listener = FileListenerStep(
            logger=logger,
            competition_code=config.competition_code,
            files_path=config.websocket_path,
            message_source=MessageSource.SOURCE_WS_LISTENER,
            next_step=parsers_pipe,
        )
    else:
        raise Exception('It must be provided a path or a websocket URI')

    return ws_listener


def _build_notifications_process(
        config: WsParserConfig,
        logger: Logger,
        auth_data: AuthData,
        competitions: DictProxy) -> StartStep:
    """Build process with notifications listener."""
    mapper = NotificationMapperStep(
        logger=logger,
        map_notification={
            NotificationType: CompetitionInfoRefreshStep(
                logger=logger,
                api_lts=config.api_lts,
                auth_data=auth_data,
                competitions=competitions,  # type: ignore
            ),
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
        config: WsParserConfig,
        logger: Logger,
        competitions: DictProxy,
        next_step: MidStep) -> WsParsersStep:  # noqa
    """Build pipe with data parsers."""
    initial_parser = InitialDataParser()
    parsers: List[Parser] = [
        CompetitionMetadataRemainingParser(competitions),  # type: ignore
        CompetitionMetadataStatusParser(competitions),  # type: ignore
        DriverNameParser(competitions),  # type: ignore
        PitInParser(competitions),  # type: ignore
        PitOutParser(competitions),  # type: ignore
        TeamNameParser(competitions),  # type: ignore
        TimingBestTimeParser(competitions),  # type: ignore
        TimingLapParser(competitions),  # type: ignore
        TimingLastTimeParser(competitions),  # type: ignore
        TimingNumberPitsParser(competitions),  # type: ignore
        TimingPitTimeParser(competitions),  # type: ignore
        TimingPositionParser(competitions),  # type: ignore
    ]

    unknowns_storage = MessageStorageStep(
        logger=logger,
        output_path=config.unknowns_path,
    )
    parser_step = WsParsersStep(
        logger=logger,
        initial_parser=initial_parser,
        parsers=parsers,
        on_parsed=next_step,
        on_unknown=unknowns_storage,
    )
    return parser_step


def _build_action_handlers(
        config: WsParserConfig,
        auth_data: AuthData,
        competitions: DictProxy) -> Dict[ActionType, ApiHandler]:
    """Build map of handlers applied to action types."""
    return {
        ActionType.ADD_PIT_IN: AddPitInHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.ADD_PIT_OUT: AddPitOutHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.INITIALIZE: InitialDataHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_DRIVER: UpdateDriverHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_COMPETITION_METADATA_REMAINING: UpdateCompetitionMetadataRemainingHandler(  # noqa: E501, LN001
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_COMPETITION_METADATA_STATUS: UpdateCompetitionMetadataStatusHandler(  # noqa: E501, LN001
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TEAM: UpdateTeamHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_BEST_TIME: UpdateTimingBestTimeHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_LAP: UpdateTimingLapHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_LAST_TIME: UpdateTimingLastTimeHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_NUMBER_PITS: UpdateTimingNumberPitsHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_PIT_TIME: UpdateTimingPitTimeHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
        ActionType.UPDATE_TIMING_POSITION: UpdateTimingPositionHandler(
            api_url=config.api_lts.strip('/'),
            auth_data=auth_data,
            competitions=competitions,  # type: ignore
        ),
    }
