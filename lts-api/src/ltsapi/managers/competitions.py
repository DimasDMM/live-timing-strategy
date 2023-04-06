from logging import Logger
from typing import List

from ltsapi.db import DBContext
from ltsapi.models.responses import FullCompetition


class CompetitionManager:
    """Manage data of competitions."""

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[FullCompetition]:
        """Get all competitions in the database."""
        with self._db as cursor:
            query = '''
                SELECT
                    cidx.`id` AS cidx_id,
                    cidx.`track_id` AS cidx_track_id,
                    cidx.`name` AS cidx_name,
                    cidx.`description` AS cidx_description,
                    cidx.`code` AS cidx_code,
                    cidx.`insert_date` AS cidx_insert_date,
                    cidx.`update_date` AS cidx_update_date,
                    tracks.`id` AS tracks_id,
                    tracks.`name` AS tracks_name,
                    tracks.`insert_date` AS tracks_insert_date,
                    tracks.`update_date` AS tracks_update_date
                FROM competitions_index as cidx
                JOIN tracks ON tracks.id = cidx.track_id'''
            cursor.execute(query)  # type: ignore
            raw_data: List[dict] = cursor.fetchall()  # type: ignore
            items: List[FullCompetition] = []
            for row in raw_data:
                items.append(FullCompetition(
                    id=row['cidx_id'],
                    track={
                        'id': row['tracks_id'],
                        'name': row['tracks_name'],
                        'insert_date': row['tracks_insert_date'],
                        'update_date': row['tracks_update_date'],
                    },
                    code=row['cidx_code'],
                    name=row['cidx_name'],
                    description=row['cidx_description'],
                    insert_date=row['cidx_insert_date'],
                    update_date=row['cidx_update_date'],
                ))
            return items
