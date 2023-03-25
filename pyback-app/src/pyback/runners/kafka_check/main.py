import logging
import msgpack  # type: ignore
import sys

from pyback.configs import TestKafkaConfig
from pyback.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from pyback.steps.loggers import LogInfoStep
from pyback.steps.dummy import DummyStartStep
from pyback.runners import BANNER_MSG


MODE_CONSUMER = 'consumer'
MODE_PRODUCER = 'producer'
TEST_GROUP = 'test-group'
TEST_TOPIC = 'test-topic'


def main(
        config: TestKafkaConfig,
        logger: logging.Logger) -> None:
    """
    Check that Kafka works correctly.

    Params:
        config (TestKafkaConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    if config.test_mode not in [MODE_CONSUMER, MODE_PRODUCER]:
        logger.error(
            f'Test mode must be "{MODE_CONSUMER}" or "{MODE_PRODUCER}".')
        sys.exit(1)

    logger.info(f'Test mode: {config.test_mode}')
    logger.debug(f'Group ID: {TEST_GROUP}')
    logger.debug(f'Topic: {TEST_TOPIC}')

    if config.test_mode == MODE_CONSUMER:
        # Consumer mode: it just prints the data on the console
        logger.info('Init script...')
        log_step = LogInfoStep(logger)
        kafka_consumer = KafkaConsumerStep(
            bootstrap_servers=config.kafka_servers,
            topics=[TEST_TOPIC],
            value_deserializer=msgpack.loads,
            next_step=log_step,
            group_id=TEST_GROUP,
        )
        logger.info('Start consumer...')
        kafka_consumer.start_step()
    else:
        # Producer mode: it generates dummy messages
        logger.info('Init script...')
        kafka_producer = KafkaProducerStep(
            logger=logger,
            bootstrap_servers=config.kafka_servers,
            topic=TEST_TOPIC,
            value_serializer=msgpack.dumps,
        )
        dummy_generator = DummyStartStep(next_step=kafka_producer)
        logger.info('Start producer...')
        dummy_generator.start_step()
        logger.info('Finish producer...')
