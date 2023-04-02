import logging
import msgpack  # type: ignore

from pyback.configs import WsListenerConfig
from pyback.runners import BANNER_MSG
from pyback.steps.listeners import WebsocketListenerStep
from pyback.steps.kafka import KafkaProducerStep


def main(
        config: WsListenerConfig,
        logger: logging.Logger) -> None:
    """
    Process to listen incoming data from a websocket.

    Params:
        config (WsListenerConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info('Init script...')
    logger.info(f'Competition code: {config.competition_code}')
    logger.debug(f'Topic: {config.kafka_topic}')
    kafka_producer = KafkaProducerStep(
        logger,
        bootstrap_servers=config.kafka_servers,
        topic=config.kafka_topic,
        value_serializer=msgpack.dumps,
    )
    ws_listener = WebsocketListenerStep(
        logger,
        competition_code=config.competition_code,
        uri=config.websocket_uri,
        next_step=kafka_producer,
    )

    logger.info('Start websocket listener...')
    ws_listener.start_step()
