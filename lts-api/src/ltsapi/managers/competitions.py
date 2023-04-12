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
from ltsapi.models.competitions import (
    AddCompetition,
    GetCompetition,
    GetCompetitionSettings,
    AddTrack,
    GetTrack,
    UpdateCompetitionSettings,
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

    def _raw_to_track(
            self, row: dict) -> GetTrack:
        """Build an instance of GetTrack."""
        return GetTrack(
            id=row['track_id'],
            name=row['track_name'],
            insert_date=row['track_insert_date'],
            update_date=row['track_update_date'],
        )


class CSettingsManager:
    """Manage settings of competitions."""

    BASE_QUERY = '''
        SELECT
            cs.`length` AS cs_length,
            cs.`length_unit` AS cs_length_unit,
            cs.`pit_time` AS cs_pit_time,
            cs.`min_number_pits` AS cs_min_number_pits,
            cs.`insert_date` AS cs_insert_date,
            cs.`update_date` AS cs_update_date
        FROM competitions_settings as cs'''
    TABLE_NAME = 'competitions_settings'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_by_id(
            self, competition_id: int) -> Optional[GetCompetitionSettings]:
        """
        Retrieve the settings of a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            GetCompetitionSettings | None: If the competition exists, returns
                its instance.
        """
        query = f'{self.BASE_QUERY} WHERE cs.competition_id = %s'
        model: Optional[GetCompetitionSettings] = fetchone_model(  # type: ignore
            self._db, self._raw_to_settings, query, (competition_id,))
        return model

    def update_by_id(
            self,
            settings: UpdateCompetitionSettings,
            competition_id: int,
            commit: bool = True) -> None:
        """
        Update the settings of a competition (it must already exist).

        Params:
            settings (UpdateCompetitionSettings): New settings of the
                competition ('None' is ignored).
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.
        """
        if self.get_by_id(competition_id) is None:
            raise ApiError(
                message=(f'The competition with ID={competition_id} '
                         'does not exist.'),
                status_code=400)
        update_model(
            self._db,
            self.TABLE_NAME,
            settings.dict(),
            key_name='competition_id',
            key_value=competition_id,
            commit=commit)

    def _raw_to_settings(
            self, row: dict) -> GetCompetitionSettings:
        """Build an instance of GetCompetitionSettings."""
        return GetCompetitionSettings(
            length=row['cs_length'],
            length_unit=row['cs_length_unit'],
            pit_time=row['cs_pit_time'],
            min_number_pits=row['cs_min_number_pits'],
            insert_date=row['cs_insert_date'],
            update_date=row['cs_update_date'],
        )


class CompetitionsIndexManager:
    """Manage data of competitions."""

    BASE_QUERY = '''
        SELECT
            cidx.`id` AS cidx_id,
            cidx.`track_id` AS cidx_track_id,
            cidx.`name` AS cidx_name,
            cidx.`description` AS cidx_description,
            cidx.`competition_code` AS cidx_competition_code,
            cidx.`insert_date` AS cidx_insert_date,
            cidx.`update_date` AS cidx_update_date,
            tracks.`id` AS tracks_id,
            tracks.`name` AS tracks_name,
            tracks.`insert_date` AS tracks_insert_date,
            tracks.`update_date` AS tracks_update_date
        FROM competitions_index as cidx
        JOIN tracks ON tracks.id = cidx.track_id'''
    TABLE_NAME = 'competitions_index'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetCompetition]:
        """Get all competitions in the database."""
        models: List[GetCompetition] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_competition, self.BASE_QUERY)
        return models

    def get_by_id(self, competition_id: int) -> Optional[GetCompetition]:
        """
        Retrieve a competition by its ID.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            GetCompetition | None: If the competition exists, returns
                its instance.
        """
        query = f'{self.BASE_QUERY} WHERE cidx.id = %s'
        model: Optional[GetCompetition] = fetchone_model(  # type: ignore
            self._db, self._raw_to_competition, query, (competition_id,))
        return model

    def get_by_code(self, competition_code: str) -> Optional[GetCompetition]:
        """
        Retrieve a competition by its code.

        Params:
            competition_code (str): Code of the competition.

        Returns:
            GetCompetition | None: If the competition exists, returns
                its instance.
        """
        query = f'{self.BASE_QUERY} WHERE cidx.competition_code = %s'
        model: Optional[GetCompetition] = fetchone_model(  # type: ignore
            self._db, self._raw_to_competition, query, (competition_code,))
        return model

    def add_one(
            self,
            competition: AddCompetition,
            commit: bool = True) -> Optional[int]:
        """
        Add a new competition.

        Params:
            competition (AddCompetition): Data of the competition.
            commit (bool): Commit transaction.

        Returns:
            int | None: ID of inserted model.
        """
        code = competition.competition_code
        if self.get_by_code(code) is not None:
            raise ApiError(
                message=(
                    f'There is already a competition with the code "{code}".'),
                status_code=400)

        model_data = competition.dict(exclude={'settings'})
        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=False)

        model_data = competition.settings.dict()
        model_data['competition_id'] = item_id
        _ = insert_model(
            self._db, CSettingsManager.TABLE_NAME, model_data, commit=commit)

        return item_id

    def _raw_to_competition(
            self, row: dict) -> GetCompetition:
        """Build an instance of GetCompetition."""
        return GetCompetition(
            id=row['cidx_id'],
            track={
                'id': row['tracks_id'],
                'name': row['tracks_name'],
                'insert_date': row['tracks_insert_date'],
                'update_date': row['tracks_update_date'],
            },
            competition_code=row['cidx_competition_code'],
            name=row['cidx_name'],
            description=row['cidx_description'],
            insert_date=row['cidx_insert_date'],
            update_date=row['cidx_update_date'],
        )
