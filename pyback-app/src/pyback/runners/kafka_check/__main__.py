#!/usr/bin/python

import argparse

from pyback.runners import build_logger
from pyback.runners.kafka_check.main import main
from pyback.configs import KafkaCheckConfig
from pyback.configs import (
    DEFAULT_TEST_GROUP,
    DEFAULT_TEST_TOPIC,
    DEFAULT_VERBOSITY,
)


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the test kafka script.')
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='File that contains the credentials.',
    required=True)
parser.add_argument(
    '--kafka_topic',
    type=str,
    help='Kafka topic to suscribe.',
    default=DEFAULT_TEST_TOPIC)
parser.add_argument(
    '--kafka_group',
    type=str,
    help='Suscribe to the topic with a specific group name.',
    default=DEFAULT_TEST_GROUP)
parser.add_argument(
    '--test_mode',
    help='Test mode: "consumer" or "producer".',
    type=str,
    required=True)
parser.add_argument(
    '--verbosity',
    help='Level of verbosity of messages.',
    type=int,
    default=DEFAULT_VERBOSITY)

args = {key: value for key, value in vars(parser.parse_args()).items()
        if value is not None}
config = KafkaCheckConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
