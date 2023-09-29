#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.ws_raw_storage.main import main
from ltspipe.configs import WsRawStorageConfig
from ltspipe.configs import (
    DEFAULT_WS_RAW_DATA_PATH,
    DEFAULT_WS_RAW_ERRORS_PATH,
    DEFAULT_VERBOSITY,
)


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the raw storage script.')
parser.add_argument(
    '--competition_code',
    type=str,
    help='Verbose code to identify the competition.',
    required=True)
parser.add_argument(
    '--errors_path',
    type=str,
    help='Path to store errors on running time.',
    default=DEFAULT_WS_RAW_ERRORS_PATH)
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
parser.add_argument(
    '--output_path',
    type=str,
    help='Path to store the raw data.',
    default=DEFAULT_WS_RAW_DATA_PATH)
parser.add_argument(
    '--websocket_uri',
    type=str,
    help='URI of websocket to listen for incoming data.',
    required=True)
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = WsRawStorageConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
