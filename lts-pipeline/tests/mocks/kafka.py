from kafka import KafkaProducer  # type: ignore
from kafka.producer.future import FutureRecordMetadata  # type: ignore
from typing import Any, Dict, Optional


class MockKafkaProducer(KafkaProducer):
    """Mock of kafka.KafkaProducer."""

    def __init__(self, **kwargs: dict) -> None:  # noqa: U100
        """Construct."""
        self._values: Dict[str, list] = {}

    def get_values(self) -> Dict[str, list]:
        """Return received values."""
        return self._values

    def send(
        self,
        topic: str,
        value: Optional[Any] = None,
        key: Optional[Any] = None,  # noqa: U100
        headers: Optional[Any] = None,  # noqa: U100
        partition: Optional[int] = None,  # noqa: U100
        timestamp_ms: Optional[int] = None,  # noqa: U100
    ) -> FutureRecordMetadata:
        """Mock send method."""
        if topic not in self._values:
            self._values[topic] = []
        self._values[topic].append(value)
        return MockFutureRecordMetadata()


class MockFutureRecordMetadata(FutureRecordMetadata):
    """Mock of kafka.producer.future.FutureRecordMetadata."""

    def __init__(self) -> None:
        """Construct."""
        pass  # Ignore constructor

    def get(self, timeout: Optional[int] = None) -> Optional[Any]:  # noqa: U100
        """Mock get method."""
        return True
