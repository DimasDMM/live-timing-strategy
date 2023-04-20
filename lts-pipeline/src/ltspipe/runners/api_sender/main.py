from logging import Logger
import msgpack
from multiprocessing import Manager, Process
from multiprocessing.managers import DictProxy
import os

from ltspipe.data.actions import ActionType
from ltspipe.data.notifications import NotificationType
from ltspipe.configs import ApiSenderConfig
from ltspipe.api.handlers import InitialDataHandler
from ltspipe.steps.api import CompetitionInfoInitStep, ApiActionStep
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.mappers import NotificationMapperStep
from ltspipe.steps.triggers import ActionInitTriggerStep
from ltspipe.runners import BANNER_MSG


def main(config: ApiSenderConfig, logger: Logger) -> None:
    """
    Process to parse raw messages.

    Params:
        config (ApiSenderConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.debug(f'Topic consumer: {config.kafka_consume}')

    with Manager() as manager:
        logger.info('Init script...')
        competitions = manager.dict()
        std_consumer = _build_std_process(config, logger, competitions)
        notification_listener = _build_notifications_process(
            config, logger, competitions)

        logger.info('Start notifications listener...')
        p_not = Process(
            target=notification_listener.start_step())  # type: ignore
        p_not.start()

        logger.info('Start standard-data consumer...')
        p_raw = Process(target=std_consumer.start_step())  # type: ignore
        p_raw.start()

        p_not.join()
        p_raw.join()


def _build_std_process(
        config: ApiSenderConfig,
        logger: Logger,
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
                competitions=competitions,  # type: ignore
            ),
        },
        next_step=init_trigger,
    )
    info_init = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
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
        competitions: DictProxy) -> KafkaConsumerStep:
    """Build process with notifications listener."""
    api_getter = CompetitionInfoInitStep(
        logger=logger,
        api_lts=config.api_lts.strip('/'),
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
