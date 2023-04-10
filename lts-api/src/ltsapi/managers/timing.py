from logging import Logger

from ltsapi.db import DBContext


class TimingManager:
    """Manage data of times."""

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger
