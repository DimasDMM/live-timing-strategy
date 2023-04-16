from kafka import KafkaConsumer, KafkaProducer  # type: ignore
from kafka.producer.future import FutureRecordMetadata  # type: ignore
from typing import Any, Dict, List, Optional


class MockKafkaRecord:
    """Mock of returned type by KafkaConsumer."""

    value: Any

    def __init__(self, value: Any) -> None:
        """Construct."""
        self.value = value


class MockKafkaConsumer(KafkaConsumer):
    """Mock of kafka.KafkaConsumer."""

    def __init__(self, messages: List[str]) -> None:  # noqa: U100
        """Construct."""
        self._messages = messages
        self.__iter__()

    def __iter__(self) -> Any:
        """Initialize iterator."""
        self._i = 0
        return self

    def __next__(self) -> MockKafkaRecord:
        """Mock consumer."""
        if self._i >= len(self._messages):
            raise StopIteration
        x = self._messages[self._i]
        self._i += 1
        return MockKafkaRecord(value=x)


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
