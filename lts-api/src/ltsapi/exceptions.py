

class ApiError(Exception):
    """Wrapper of API exception."""

    def __init__(self, *args: object) -> None:
        """Construct."""
        super().__init__(*args)
