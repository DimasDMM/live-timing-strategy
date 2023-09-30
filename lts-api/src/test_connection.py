from typing import List

from ltsapi import _build_logger
from ltsapi.router import _build_db_connection
from ltsapi.models.competitions import GetCompetition
from ltsapi.models.tracks import GetTrack


if __name__ == '__main__':
    """Check that connection with the database works correctly."""
    logger = _build_logger(__package__)
    db = _build_db_connection(logger=logger)
    with db as cursor:
        query = '''
            SELECT
                cidx.`id` AS cidx_id,
                cidx.`track_id` AS cidx_track_id,
                cidx.`name` AS cidx_name,
                cidx.`code` AS cidx_code,
                cidx.`description` AS cidx_description,
                cidx.`insert_date` AS cidx_insert_date,
                cidx.`update_date` AS cidx_update_date,
                tracks.`id` AS tracks_id,
                tracks.`name` AS tracks_name,
                tracks.`insert_date` AS tracks_insert_date,
                tracks.`update_date` AS tracks_update_date
            FROM competitions_index as cidx
            JOIN tracks ON tracks.id = cidx.track_id
            LIMIT 5'''
        cursor.execute(query)  # type: ignore
        raw_data: List[dict] = cursor.fetchall()  # type: ignore
        for row in raw_data:
            item = GetCompetition(
                id=row['cidx_id'],
                track=GetTrack(
                    id=row['tracks_id'],
                    name=row['tracks_name'],
                    insert_date=row['tracks_insert_date'],
                    update_date=row['tracks_update_date'],
                ),
                competition_code=row['cidx_code'],
                name=row['cidx_name'],
                description=row['cidx_description'],
                insert_date=row['cidx_insert_date'],
                update_date=row['cidx_update_date'],
            )
            logger.info(item)
    logger.info('Finish!')
