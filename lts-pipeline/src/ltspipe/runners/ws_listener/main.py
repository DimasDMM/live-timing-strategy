import logging
import msgpack  # type: ignore
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy

from ltspipe.configs import WsListenerConfig
from ltspipe.data.enum import FlagName
from ltspipe.data.notifications import NotificationType
from ltspipe.runners import BANNER_MSG
from ltspipe.steps.bulk import (
    QueueDistributorStep,
    QueueForwardStep,
)
from ltspipe.steps.listeners import WebsocketListenerStep
from ltspipe.steps.notifications import (
    FlagModifierStep,
    NotificationMapperStep,
)
from ltspipe.steps.triggers import WsInitTriggerStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep


def main(config: WsListenerConfig, logger: logging.Logger) -> None:
    """
    Process to listen incoming data from a websocket.

    Params:
        config (WsListenerConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Competition code: {config.competition_code}')
    logger.debug(f'Topic producer: {config.kafka_produce}')

    with Manager() as manager:
        logger.info('Init script...')
        flags = manager.dict()
        queue = manager.dict()
        ws_listener = _build_websocket_process(
            config, logger, flags, queue)
        notification_listener = _build_notifications_process(
            config, logger, flags, queue)

        logger.info('Start notifications listener...')
        p_not = Process(
            target=notification_listener.start_step())  # type: ignore
        p_not.start()

        logger.info('Start websocket listener...')
        p_ws = Process(target=ws_listener.start_step())  # type: ignore
        p_ws.start()

        p_not.join()
        p_ws.join()


def _build_notifications_process(
        config: WsListenerConfig,
        logger: logging.Logger,
        flags: DictProxy,
        queue: DictProxy) -> KafkaConsumerStep:
    """Build process with notifications listener."""
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


def _build_websocket_process(
        config: WsListenerConfig,
        logger: logging.Logger,
        flags: DictProxy,
        queue: DictProxy) -> WebsocketListenerStep:
    """Build process with websocket listener."""
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
    ws_listener = WebsocketListenerStep(
        logger,
        competition_code=config.competition_code,
        uri=config.websocket_uri,
        next_step=queue_distributor,
    )

    return ws_listener
