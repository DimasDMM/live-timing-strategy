#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.parser.main import main
from ltspipe.configs import ParserConfig
from ltspipe.configs import (
    DEFAULT_NOTIFICATIONS_TOPIC,
    DEFAULT_PARSER_GROUP,
    DEFAULT_PARSER_ERRORS_PATH,
    DEFAULT_PARSER_UNKNOWNS_PATH,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_STD_MESSAGES_TOPIC,
    DEFAULT_VERBOSITY,
)


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the parser script.')
parser.add_argument(
    '--api_lts',
    type=str,
    help='URI of API REST of LTS app.',
    required=True)
parser.add_argument(
    '--errors_path',
    type=str,
    help='Path to store errors on running time.',
    default=DEFAULT_PARSER_ERRORS_PATH)
parser.add_argument(
    '--kafka_consume',
    type=str,
    help='Kafka topic to consume.',
    default=DEFAULT_RAW_MESSAGES_TOPIC)
parser.add_argument(
    '--kafka_group',
    type=str,
    help='Suscribe to the topic with a specific group name.',
    default=DEFAULT_PARSER_GROUP)
parser.add_argument(
    '--kafka_notifications',
    type=str,
    help='Kafka topic to write and read notifications.',
    default=DEFAULT_NOTIFICATIONS_TOPIC)
parser.add_argument(
    '--kafka_produce',
    type=str,
    help='Kafka topic to write data.',
    default=DEFAULT_STD_MESSAGES_TOPIC)
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
parser.add_argument(
    '--unknowns_path',
    type=str,
    help='Path to store unknown messages during parsing.',
    default=DEFAULT_PARSER_UNKNOWNS_PATH)
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = ParserConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
