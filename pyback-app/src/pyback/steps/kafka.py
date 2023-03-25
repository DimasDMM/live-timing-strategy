import logging
from kafka import (  # type: ignore
    KafkaConsumer as _KafkaConsumer,
    KafkaProducer as _KafkaProducer,
)
from kafka.errors import KafkaError  # type: ignore
from kafka.producer.future import FutureRecordMetadata  # type: ignore
from typing import Any, Callable, List, Optional

from pyback.messages import Message
from pyback.steps.base import StartStep, MidStep


class KafkaConsumerStep(StartStep):
    """Step that acts as a wrapper of kafka.KafkaConsumer."""

    def __init__(
            self,
            bootstrap_servers: List[str],
            topics: List[str],
            value_deserializer: Callable,
            next_step: MidStep,
            group_id: Optional[str] = None) -> None:
        """
        Construct.

        Params:
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
        """
        self._next_step = next_step
        self._consumer = _KafkaConsumer(
            *topics,
            bootstrap_servers=bootstrap_servers,
            group_id=group_id,
            value_deserializer=value_deserializer)

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        return [self._next_step] + self._next_step.get_children()

    def start_step(self) -> None:
        """Start listening to Kafka broker for new messages."""
        for data in self._consumer:
            msg: Message = Message.decode(data.value)
            msg.updated()
            self._next_step.run_step(msg)


class KafkaProducerStep(MidStep):
    """Step that acts as a wrapper of kafka.KafkaProducer."""

    def __init__(
            self,
            logger: logging.Logger,
            bootstrap_servers: List[str],
            topic: str,
            value_serializer: Callable,
            next_step: Optional[MidStep] = None,
            on_error_step: Optional[MidStep] = None,
            timeout: int = 5) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            bootstrap_servers (List[str]): List of 'host[:port]' strings that
                the consumer should contact to bootstrap initial cluster
                metadata. This does not have to be the full node list.
            topic (str): Topics where the messages will be published.
            value_serializer (Callable): Any callable that takes a raw message
                value and serializes it.
            next_step (MidStep): Optionally, apply another step to the message.
            timeout (str | None): Timeout to send a message.
        """
        self._logger = logger
        self._topic = topic
        self._next_step = next_step
        self._on_error_step = on_error_step
        self._timeout = timeout
        self._producer = _KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=value_serializer,
        )

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        children = []
        if self._next_step is not None:
            children += [self._next_step] + self._next_step.get_children()
        if self._on_error_step is not None:
            children += (
                [self._on_error_step] + self._on_error_step.get_children())
        return children

    def run_step(self, msg: Message) -> None:
        """Send messages to Kafka."""
        future: FutureRecordMetadata = self._producer.send(
            topic=self._topic, value=str(msg))
        try:
            _ = future.get(timeout=self._timeout)
            if self._next_step is not None:
                self._next_step.run_step(msg)
        except KafkaError as e:
            self._logger.critical(e, exc_info=True)
            if self._on_error_step is not None:
                self._on_error_step.run_step(msg)
