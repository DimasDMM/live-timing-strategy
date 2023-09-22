from datetime import datetime
from logging import Logger
from kafka import (  # type: ignore
    KafkaConsumer as _KafkaConsumer,
    KafkaProducer as _KafkaProducer,
)
from kafka.errors import KafkaError  # type: ignore
from kafka.producer.future import FutureRecordMetadata  # type: ignore
import traceback
from typing import Any, Callable, List, Optional

from ltspipe.messages import Message
from ltspipe.steps.base import StartStep, MidStep


class KafkaConsumerStep(StartStep):
    """Step that acts as a wrapper of kafka.KafkaConsumer."""

    def __init__(
            self,
            logger: Logger,
            bootstrap_servers: List[str],
            topics: List[str],
            value_deserializer: Callable,
            next_step: MidStep,
            group_id: Optional[str] = None,
            on_error: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (Logger): Logger instance to display information.
            bootstrap_servers (List[str]): list of 'host[:port]' strings that
                the consumer should contact to bootstrap initial cluster
                metadata. This does not have to be the full node list.
            topics (List[str]): List of topics to subscribe to.
            value_deserializer (Callable): Any callable that takes a raw message
                value and returns a deserialized value.
            next_step (MidStep): The next step to apply to the message.
            group_id (str | None): The name of the consumer group to join for
                dynamic partition assignment (if enabled), and to use for
                fetching and committing offsets. If None, auto-partition
                assignment and offset commits are disabled.
            on_error (MidStep | None): Optionally, apply another step to the
                message if there is any error on running time.
        """
        self._logger = logger
        self._next_step = next_step
        self._on_error = on_error
        self._consumer = self._build_kafka_consumer(
            topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=value_deserializer)

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = [self._next_step] + self._next_step.get_children()
        if self._on_error is not None:
            children += [self._on_error] + self._on_error.get_children()
        return children

    def start_step(self) -> None:
        """Start listening to Kafka broker for new messages."""
        for data in self._consumer:
            try:
                msg: Message = Message.decode(data.value)
                self._logger.info(f'Kafka data: {msg}')
                msg.updated()
                self._next_step.run_step(msg)
            except Exception as e:
                self._logger.critical(e, exc_info=True)
                if self._on_error is not None:
                    msg = Message(
                        competition_code=msg.competition_code,
                        data=msg.data,
                        source=msg.source,
                        decoder=msg.decoder,
                        created_at=datetime.utcnow().timestamp(),
                        updated_at=datetime.utcnow().timestamp(),
                        error_description=str(e),
                        error_traceback=traceback.format_exc(),
                    )
                    msg.updated()
                    self._on_error.run_step(msg)

    def _build_kafka_consumer(
            self,
            topics: List[str],
            bootstrap_servers: List[str],
            group_id: Optional[str],
            value_deserializer: Callable) -> _KafkaConsumer:
        """Wrap builder of KafkaConsumer."""
        return _KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=value_deserializer,
        )


class KafkaProducerStep(MidStep):
    """Step that acts as a wrapper of kafka.KafkaProducer."""

    def __init__(
            self,
            logger: Logger,
            bootstrap_servers: List[str],
            topic: str,
            value_serializer: Callable,
            next_step: Optional[MidStep] = None,
            on_error: Optional[MidStep] = None,
            timeout: int = 5) -> None:
        """
        Construct.

        Params:
            logger (Logger): Logger instance to display information.
            bootstrap_servers (List[str]): List of 'host[:port]' strings that
                the consumer should contact to bootstrap initial cluster
                metadata. This does not have to be the full node list.
            topic (str): Topics where the messages will be published.
            value_serializer (Callable): Any callable that takes a raw message
                value and serializes it.
            next_step (MidStep | None): Optionally, apply another step to the
                message.
            timeout (str | None): Timeout to send a message.
        """
        self._logger = logger
        self._topic = topic
        self._next_step = next_step
        self._on_error = on_error
        self._timeout = timeout
        self._producer = self._build_kafka_producer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=value_serializer,
        )

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._next_step is not None:
            children += [self._next_step] + self._next_step.get_children()
        if self._on_error is not None:
            children += (
                [self._on_error] + self._on_error.get_children())
        return children

    def run_step(self, msg: Message) -> None:
        """Run step."""
        future: FutureRecordMetadata = self._producer.send(
            topic=self._topic, value=str(msg))
        try:
            _ = future.get(timeout=self._timeout)
            if self._next_step is not None:
                msg.updated()
                self._next_step.run_step(msg)
        except KafkaError as e:
            self._logger.critical(e, exc_info=True)
            if self._on_error is not None:
                msg.updated()
                self._on_error.run_step(msg)

    def _build_kafka_producer(
            self,
            bootstrap_servers: List[str],
            value_serializer: Callable) -> _KafkaProducer:
        """Wrap builder of KafkaProducer."""
        return _KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=value_serializer,
        )
