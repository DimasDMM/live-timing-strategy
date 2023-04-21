from ltsapi.models.responses import ErrorResponse


class ApiError(Exception):
    """Wrapper of API exception."""

    def __init__(
            self,
            message: str,
            status_code: int = 400,
            *args: object) -> None:
        """Construct."""
        self._message = message
        self._status_code = status_code
        super().__init__(*args)

    def get_message(self) -> str:
        """Return error message."""
        return self._message

    def get_status_code(self) -> int:
        """Return HTTP status code."""
        return self._status_code

    def error_response(self) -> ErrorResponse:
        """Transform exception into a response model."""
        return ErrorResponse(
            status_code=self.get_status_code(),
            message=self.get_message(),
            extra_data={},
        )

    def __str__(self) -> str:
        """Transform the exception into a string."""
        return self._message
