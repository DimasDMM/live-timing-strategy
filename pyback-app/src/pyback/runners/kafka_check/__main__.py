#!/usr/bin/python

import argparse

from pyback.runners import build_logger
from pyback.runners.kafka_check.main import main
from pyback.configs import TestKafkaConfig
from pyback.configs import DEFAULT_VERBOSITY


parser = argparse.ArgumentParser(
    conflict_handler='resolve',
    description='Arguments of the test kafka script.')
parser.add_argument(
    '--kafka_servers',
    nargs='+',
    help='File that contains the credentials.',
    required=True)
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
config = TestKafkaConfig(**args)
logger = build_logger(__package__, config.verbosity)

try:
    main(config, logger)
except Exception as e:
    logger.critical(e, exc_info=True)
    exit(1)
