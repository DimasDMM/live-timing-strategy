#!/usr/bin/python

import argparse

from pyback.runners import build_logger
from pyback.runners.ws_listener.main import main
from pyback.configs import WsListenerConfig
from pyback.configs import (
    DEFAULT_RAW_MESSAGES_TOPIC,
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
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
parser.add_argument(
    '--kafka_topic',
    type=str,
    help='Kafka topic to suscribe.',
    default=DEFAULT_RAW_MESSAGES_TOPIC)
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
