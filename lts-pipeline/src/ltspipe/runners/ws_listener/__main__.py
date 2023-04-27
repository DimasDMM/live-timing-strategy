#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.ws_listener.main import main
from ltspipe.configs import WsListenerConfig
from ltspipe.configs import (
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_VERBOSITY,
    DEFAULT_WS_ERRORS_PATH,
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
    default=DEFAULT_WS_ERRORS_PATH)
parser.add_argument(
    '--kafka_notifications',
    type=str,
    help='Kafka topic to write and read notifications.',
    default=DEFAULT_NOTIFICATIONS_TOPIC)
parser.add_argument(
    '--kafka_produce',
    type=str,
    help='Kafka topic to write data.',
    default=DEFAULT_RAW_MESSAGES_TOPIC)
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
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
config = WsListenerConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
