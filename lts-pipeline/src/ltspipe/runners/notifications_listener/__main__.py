#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.notifications_listener.main import main
from ltspipe.configs import NotificationsListenerConfig
from ltspipe.configs import (
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_NOTIFICATIONS_LISTENER_GROUP,
    DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH,
    DEFAULT_VERBOSITY,
)


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the notifications listener script.')
parser.add_argument(
    '--api_lts',
    type=str,
    help='URI of API REST of LTS app.',
    required=True)
parser.add_argument(
    '--competition_code',
    type=str,
    help='Verbose code to identify the competition.',
    required=True)
parser.add_argument(
    '--errors_path',
    type=str,
    help='Path to store errors on running time.',
    default=DEFAULT_NOTIFICATIONS_LISTENER_ERRORS_PATH)
parser.add_argument(
    '--kafka_group',
    type=str,
    help='Suscribe to the topic with a specific group name.',
    default=DEFAULT_NOTIFICATIONS_LISTENER_GROUP)
parser.add_argument(
    '--kafka_notifications',
    type=str,
    help='Kafka topic to write and read notifications.',
    default=DEFAULT_NOTIFICATIONS_TOPIC)
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = NotificationsListenerConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
