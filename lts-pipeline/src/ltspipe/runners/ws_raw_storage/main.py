import logging
import os

from ltspipe.configs import WsRawStorageConfig
from ltspipe.steps.filesystem import MessageStorageStep, RawStorageStep
from ltspipe.steps.listeners import WebsocketListenerStep
from ltspipe.runners import BANNER_MSG


def main(
        config: WsRawStorageConfig,
        logger: logging.Logger) -> None:
    """
    Process to store raw messages.

    Params:
        config (WsRawStorageConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Create path if it does not exist: {config.output_path}')
    os.makedirs(config.output_path, exist_ok=True)

    logger.info(f'Create path if it does not exist: {config.errors_path}')
    os.makedirs(config.errors_path, exist_ok=True)

    logger.info('Init processes...')
    raw_storage = RawStorageStep(
        logger=logger,
        output_path=config.output_path,
    )
    message_storage = MessageStorageStep(
        logger=logger,
        output_path=config.output_path,
        next_step=raw_storage,
    )

    errors_storage = MessageStorageStep(
        logger=logger,
        output_path=config.errors_path,
    )
    ws_listener = WebsocketListenerStep(
        logger,
        competition_code=config.competition_code,
        uri=config.websocket_uri,
        next_step=message_storage,
        on_error=errors_storage,
    )

    logger.info('Processes created')

    logger.info('Start websocket listener...')
    ws_listener.start_step()
