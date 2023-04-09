from logging import Logger
import os

from ltsapi.db import DBContext


def _build_db_connection(logger: Logger) -> DBContext:
    """Build connection with the database."""
    return DBContext(
        host=os.environ.get('DB_HOST', None),
        port=os.environ.get('DB_PORT', None),
        user=os.environ.get('DB_USER', None),
        password=os.environ.get('DB_PASS', None),
        database=os.environ.get('DB_DATABASE', None),
        logger=logger,
    )
