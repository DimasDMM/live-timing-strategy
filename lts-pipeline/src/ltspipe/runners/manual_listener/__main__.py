#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.manual_listener.main import main
from ltspipe.configs import ManualListenerConfig
from ltspipe.configs import (
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_VERBOSITY,
)

DEFAULT_MESSAGE_SOURCE = 'ws-listener'


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the manual listener script.')
parser.add_argument(
    '--competition_code',
    type=str,
    help='Verbose code to identify the competition.',
    required=True)
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
    '--message_source',
    type=str,
    help='Source of the messages to mock.',
    default=DEFAULT_MESSAGE_SOURCE)
parser.add_argument(
    '--is_json',
    help=' If this flag is given, the format of the messages must be JSON.',
    action='store_true')
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = ManualListenerConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
