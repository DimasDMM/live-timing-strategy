from enum import Enum
import json
from requests.models import Response
from typing import Any, Dict, List, Union


class MockResponse(Response):
    """Mock of requests.models.Response."""

    def __init__(
            self,
            content: Union[dict, list],
            status_code: int = 200) -> None:
        """Construct."""
        self._content = content  # type: ignore
        self.status_code = status_code

    def json(self) -> Union[dict, list]:  # type: ignore
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


class MapRequestMethod(Enum):
    """Enumeration of request methods."""

    GET = 'get'
    DELETE = 'delete'
    POST = 'post'
    PUT = 'put'

    def __eq__(self, other: Any) -> bool:
        """Compare enumeration to other objects and strings."""
        if self.__class__ is other.__class__:
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Build hash of current instance."""
        return hash(self.value)


class MapRequestItem:
    """Request item."""

    url: str
    method: MapRequestMethod
    responses: List[MockResponse]

    def __init__(
            self,
            url: str,
            method: MapRequestMethod,
            responses: List[MockResponse]) -> None:
        """Construct."""
        self.url = url
        self.method = method
        self.responses = responses


class MapRequests:
    """Retrieve the appropiate response for each request."""

    ERROR_500 = MockResponse(
        content={'status_code': 500, 'message': 'Error in request'},
        status_code=500,
    )

    _requests_map: Dict[MapRequestMethod, Dict[str, MapRequestItem]]

    def __init__(self, requests_map: List[MapRequestItem]) -> None:
        """Construct."""
        self._requests_map = {x.value: {}
                              for x in MapRequestMethod._member_map_.values()}
        for r in requests_map:
            self._requests_map[r.method][r.url] = r

    def get(self, url: str) -> MockResponse:
        """Do GET request."""
        if url in self._requests_map[MapRequestMethod.GET]:
            item = self._requests_map[MapRequestMethod.GET][url]
            return item.responses.pop(0)
        return self.ERROR_500

    def delete(self, url: str) -> MockResponse:
        """Do DELETE request."""
        if url in self._requests_map[MapRequestMethod.DELETE]:
            item = self._requests_map[MapRequestMethod.DELETE][url]
            return item.responses.pop(0)
        return self.ERROR_500

    def post(self, url: str) -> MockResponse:
        """Do POST request."""
        if url in self._requests_map[MapRequestMethod.POST]:
            item = self._requests_map[MapRequestMethod.POST][url]
            return item.responses.pop(0)
        return self.ERROR_500

    def put(self, url: str) -> MockResponse:
        """Do PUT request."""
        if url in self._requests_map[MapRequestMethod.PUT]:
            item = self._requests_map[MapRequestMethod.PUT][url]
            return item.responses.pop(0)
        return self.ERROR_500
