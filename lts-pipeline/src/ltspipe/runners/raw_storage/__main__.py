#!/usr/bin/python

import argparse

from ltspipe.runners import build_logger
from ltspipe.runners.raw_storage.main import main
from ltspipe.configs import RawStorageConfig
from ltspipe.configs import (
    DEFAULT_RAW_DATA_PATH,
    DEFAULT_RAW_ERRORS_PATH,
    DEFAULT_RAW_MESSAGES_TOPIC,
    DEFAULT_RAW_STORAGE_GROUP,
    DEFAULT_VERBOSITY,
)


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the raw storage script.')
parser.add_argument(
    '--errors_path',
    type=str,
    help='Path to store errors on running time.',
    default=DEFAULT_RAW_ERRORS_PATH)
parser.add_argument(
    '--kafka_consume',
    type=str,
    help='Kafka topic to consume.',
    default=DEFAULT_RAW_MESSAGES_TOPIC)
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='List of Kafka brokers separated by commas.',
    required=True)
parser.add_argument(
    '--kafka_group',
    type=str,
    help='Suscribe to the topic with a specific group name.',
    default=DEFAULT_RAW_STORAGE_GROUP)
parser.add_argument(
    '--output_path',
    type=str,
    help='Path to store the raw data.',
    default=DEFAULT_RAW_DATA_PATH)
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = RawStorageConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
