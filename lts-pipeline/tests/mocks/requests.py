import json
from requests.models import Response


class MockResponse(Response):
    """Mock of requests.models.Response."""

    def __init__(
            self,
            content: dict,
            status_code: int = 200) -> None:
        """Construct."""
        self._content = content  # type: ignore
        self._status_code = status_code

    def json(self) -> dict:  # type: ignore
        """Return content."""
        return self._content  # type: ignore

    def __repr__(self) -> str:
        """Return representation of the instance."""
        str_content = json.dumps(self._content)
        return f'(MockResponse){str_content}'

    def __str__(self) -> str:
        """Return instance as a string."""
        str_content = json.dumps(self._content)
        return f'(MockResponse){str_content}'
