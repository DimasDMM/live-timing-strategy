from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    insert_model,
    update_model,
    fetchmany_models,
    fetchone_model,
)
from ltsapi.models.tracks import (
    AddTrack,
    GetTrack,
    UpdateTrack,
)


class TracksManager:
    """Manage the avaiable tracks."""

    BASE_QUERY = '''
        SELECT
            tracks.`id` AS track_id,
            tracks.`name` AS track_name,
            tracks.`insert_date` AS track_insert_date,
            tracks.`update_date` AS track_update_date
        FROM tracks'''
    TABLE_NAME = 'tracks'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetTrack]:
        """Get all competitions in the database."""
        models: List[GetTrack] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_track, self.BASE_QUERY)
        return models

    def get_by_id(self, track_id: int) -> Optional[GetTrack]:
        """
        Retrieve a track by its ID.

        Params:
            track_id (int): ID of the track.

        Returns:
            GetTrack | None: If the track exists, returns
                its instance.
        """
        query = f'{self.BASE_QUERY} WHERE tracks.id = %s'
        model: Optional[GetTrack] = fetchone_model(  # type: ignore
            self._db, self._raw_to_track, query, params=(track_id,))
        return model

    def add_one(self, track: AddTrack, commit: bool = True) -> Optional[int]:
        """
        Add a new track.

        Params:
            track (AddTrack): Data of the track.
            commit (bool): Commit transaction.

        Returns:
            int | None: ID of inserted model.
        """
        return insert_model(
            self._db, self.TABLE_NAME, track.dict(), commit=commit)

    def update_by_id(
            self,
            track: UpdateTrack,
            track_id: int,
            commit: bool = True) -> None:
        """
        Update the data of a track (it must already exist).

        Params:
            track (UpdateTrack): New data of the track ('None' is ignored).
            track_id (int): ID of the track.
            commit (bool): Commit transaction.
        """
        if self.get_by_id(track_id) is None:
            raise ApiError(
                message=f'The track with ID={track_id} does not exist.',
                status_code=400)
        update_model(
            self._db,
            self.TABLE_NAME,
            track.dict(),
            key_name='id',
            key_value=track_id,
            commit=commit)

    def _raw_to_track(self, row: dict) -> GetTrack:
        """Build an instance of GetTrack."""
        return GetTrack(
            id=row['track_id'],
            name=row['track_name'],
            insert_date=row['track_insert_date'],
            update_date=row['track_update_date'],
        )
