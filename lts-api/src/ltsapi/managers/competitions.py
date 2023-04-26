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
    AddCompetitionMetadata,
    GetCompetition,
    GetCompetitionMetadata,
    GetCompetitionSettings,
    UpdateCompetitionMetadata,
    UpdateCompetitionSettings,
)
from ltsapi.models.enum import (
    CompetitionStage,
    CompetitionStatus,
    LengthUnit,
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
        m: Optional[GetCompetitionSettings] = fetchone_model(  # type: ignore
            self._db, self._raw_to_settings, query, (competition_id,))
        return m

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

    def _raw_to_settings(self, row: dict) -> GetCompetitionSettings:
        """Build an instance of GetCompetitionSettings."""
        return GetCompetitionSettings(
            length=row['cs_length'],
            length_unit=row['cs_length_unit'],
            pit_time=row['cs_pit_time'],
            min_number_pits=row['cs_min_number_pits'],
            insert_date=row['cs_insert_date'],
            update_date=row['cs_update_date'],
        )


class CMetadataManager:
    """Manage metadata of competitions."""

    BASE_SELECT = '''
        SELECT
            cm.`competition_id` AS cm_competition_id,
            cm.`status` AS cm_status,
            cm.`stage` AS cm_stage,
            cm.`remaining_length` AS cm_remaining_length,
            cm.`remaining_length_unit` AS cm_remaining_length_unit,
            cm.`insert_date` AS cm_insert_date,
            cm.`update_date` AS cm_update_date'''
    CURRENT_QUERY = f'{BASE_SELECT} FROM competitions_metadata_current as cm'
    HISTORY_QUERY = f'{BASE_SELECT} FROM competitions_metadata_history as cm'
    CURRENT_TABLE = 'competitions_metadata_current'
    HISTORY_TABLE = 'competitions_metadata_history'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_current_by_id(
            self, competition_id: int) -> Optional[GetCompetitionMetadata]:
        """
        Retrieve the current metadata of a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            GetCompetitionMetadata | None: If the competition exists, returns
                its instance.
        """
        query = f'{self.CURRENT_QUERY} WHERE cm.competition_id = %s'
        m: Optional[GetCompetitionMetadata] = fetchone_model(  # type: ignore
            self._db, self._raw_to_metadata, query, (competition_id,))
        return m

    def get_history_by_id(
            self, competition_id: int) -> List[GetCompetitionMetadata]:
        """
        Retrieve the metadata history of a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetCompetitionMetadata]: History of all metadata values of the
                competition.
        """
        query = f'{self.HISTORY_QUERY} WHERE cm.competition_id = %s'
        m: List[GetCompetitionMetadata] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_metadata, query, (competition_id,))
        return m

    def update_by_id(
            self,
            metadata: UpdateCompetitionMetadata,
            competition_id: int,
            commit: bool = True) -> None:
        """
        Update the metadata of a competition (it must already exist).

        Note that, after the record is updated, it also inserts a new row in the
        history table.

        Params:
            metadata (UpdateCompetitionMetadata): New metadata of the
                competition ('None' is ignored).
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.
        """
        previous_model = self.get_current_by_id(competition_id)
        if previous_model is None:
            raise ApiError(
                message=(f'The competition with ID={competition_id} '
                         'does not exist.'),
                status_code=400)
        update_model(
            self._db,
            self.CURRENT_TABLE,
            metadata.dict(),
            key_name='competition_id',
            key_value=competition_id,
            commit=False)

        # Insert record in the history table
        new_data = metadata.dict()
        previous_data = previous_model.dict(exclude={
            'insert_date': True, 'update_date': True})
        for field_name, _ in previous_data.items():
            if new_data[field_name] is not None:
                previous_data[field_name] = new_data[field_name]
        previous_data['competition_id'] = competition_id
        _ = insert_model(
            self._db,
            CMetadataManager.HISTORY_TABLE,
            previous_data,
            commit=commit)

    def _raw_to_metadata(self, row: dict) -> GetCompetitionMetadata:
        """Build an instance of GetCompetitionMetadata."""
        return GetCompetitionMetadata(
            status=row['cm_status'],
            stage=row['cm_stage'],
            remaining_length=row['cm_remaining_length'],
            remaining_length_unit=row['cm_remaining_length_unit'],
            insert_date=row['cm_insert_date'],
            update_date=row['cm_update_date'],
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
            commit: bool = True) -> int:
        """
        Add a new competition.

        Params:
            competition (AddCompetition): Data of the competition.
            commit (bool): Commit transaction.

        Returns:
            int: ID of inserted model.
        """
        code = competition.competition_code
        if self.get_by_code(code) is not None:
            raise ApiError(
                message=(
                    f'There is already a competition with the code "{code}".'),
                status_code=400)

        model_data = competition.dict(exclude={'settings': True})
        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=False)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')

        # Create settings of the competition
        model_data = competition.settings.dict()
        model_data['competition_id'] = item_id
        _ = insert_model(
            self._db, CSettingsManager.TABLE_NAME, model_data, commit=False)

        # Create metadata of the competition
        model_data = self._initial_metadata().dict()
        model_data['competition_id'] = item_id
        _ = insert_model(
            self._db, CMetadataManager.CURRENT_TABLE, model_data, commit=False)
        _ = insert_model(
            self._db, CMetadataManager.HISTORY_TABLE, model_data, commit=commit)

        return item_id

    def _initial_metadata(self) -> AddCompetitionMetadata:
        """Create initial metadata of a competition."""
        return AddCompetitionMetadata(
            status=CompetitionStatus.PAUSED,
            stage=CompetitionStage.FREE_PRACTICE,
            remaining_length=0,
            remaining_length_unit=LengthUnit.LAPS,
        )

    def _raw_to_competition(self, row: dict) -> GetCompetition:
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
