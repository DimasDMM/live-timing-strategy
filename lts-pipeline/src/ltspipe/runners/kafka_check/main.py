import logging
import msgpack  # type: ignore

from ltspipe.configs import KafkaCheckConfig, KafkaMode
from ltspipe.steps.kafka import KafkaConsumerStep, KafkaProducerStep
from ltspipe.steps.dummy import DummyStartStep, NullStep
from ltspipe.runners import BANNER_MSG


def main(
        config: KafkaCheckConfig,
        logger: logging.Logger) -> None:
    """
    Check that Kafka works correctly.

    Params:
        config (KafkaCheckConfig): configuration to run the method.
        logger (logging.Logger): logging class.
    """
    logger.info(BANNER_MSG)
    logger.debug(config)

    logger.info(f'Test mode: {config.test_mode}')
    logger.info(f'Topic: {config.kafka_topic}')

    if config.test_mode == KafkaMode.MODE_CONSUMER:
        # Consumer mode: it just prints the data on the console
        logger.info('Init script...')
        null_step = NullStep()
        kafka_consumer = KafkaConsumerStep(
            logger=logger,
            bootstrap_servers=config.kafka_servers,
            topics=[config.kafka_topic],
            value_deserializer=msgpack.loads,
            next_step=null_step,
        )
        logger.info('Start consumer...')
        kafka_consumer.start_step()
    else:
        # Producer mode: it generates dummy messages
        logger.info('Init script...')
        kafka_producer = KafkaProducerStep(
            logger=logger,
            bootstrap_servers=config.kafka_servers,
            topic=config.kafka_topic,
            value_serializer=msgpack.dumps,
        )
        dummy_generator = DummyStartStep(next_step=kafka_producer)
        logger.info('Start producer...')
        dummy_generator.start_step()
        logger.info('Finish producer...')
