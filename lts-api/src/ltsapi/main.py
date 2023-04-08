from fastapi import FastAPI
from logging import Logger
import os
from typing import List

from ltsapi import API_VERSION, _build_logger
from ltsapi.db import DBContext
from ltsapi.managers.competitions import CompetitionManager
from ltsapi.models.competitions import GetCompetition


app = FastAPI(
    title='Live Timing Strategy',
    description='OpenAPI schema of LTS application',
    version='0.0.1',
)


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


@app.get(f'/{API_VERSION}/competitions/')
async def get_all_competitions() -> List[GetCompetition]:
    """Get all competitions in the database."""
    logger = _build_logger(__package__)
    db = _build_db_connection(logger)
    manager = CompetitionManager(db=db, logger=logger)
    return manager.get_all()
