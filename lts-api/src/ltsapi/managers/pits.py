from logging import Logger
from typing import List, Optional, Union

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    insert_model,
    update_model,
    fetchmany_models,
    fetchone_model,
)
from ltsapi.models.pits import (
    AddPitIn,
    GetPitIn,
    UpdatePitIn,
    UpdatePitInFixedKartStatus,
    UpdatePitInKartStatus,
    UpdatePitInPitTime,
)

# Alias of all fields that we may update in timing
TypeUpdatePitIn = Union[
    UpdatePitIn,
    UpdatePitInFixedKartStatus,
    UpdatePitInKartStatus,
    UpdatePitInPitTime,
]


class PitsInManager:
    """Manage the pits-in."""

    BASE_QUERY = '''
        SELECT
            pin.id AS pin_id,
            pin.competition_id AS pin_competition_id,
            pin.team_id AS pin_team_id,
            pin.driver_id AS pin_driver_id,
            pin.lap AS pin_lap,
            pin.pit_time AS pin_pit_time,
            pin.kart_status AS pin_kart_status,
            pin.fixed_kart_status AS pin_fixed_kart_status,
            pin.insert_date AS pin_insert_date,
            pin.update_date AS pin_update_date
        FROM timing_pits_in AS pin'''
    TABLE_NAME = 'timing_pits_in'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_by_competition_id(self, competition_id: int) -> List[GetPitIn]:
        """
        Get all pit-in records in a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetPitIn]: List of pits-in in the competition.
        """
        query = f'{self.BASE_QUERY} WHERE pin.competition_id = %s'
        models: List[GetPitIn] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_pit_in, query, params=(competition_id,))
        return models

    def get_by_id(
            self,
            pit_in_id: int,
            competition_id: Optional[int] = None) -> Optional[GetPitIn]:
        """
        Retrieve a pit-in by its ID.

        Params:
            pit_in_id (int): ID of the pit-in.
            competition_id (int | None): If given, the pit-in must exist in the
                competition.

        Returns:
            GetPitIn | None: If the pit-in exists, returns
                its instance.
        """
        query = f'{self.BASE_QUERY} WHERE pin.id = %s'
        params = [pit_in_id]
        if competition_id is not None:
            query = f'{query} AND pin.competition_id = %s'
            params.append(competition_id)

        model: Optional[GetPitIn] = fetchone_model(  # type: ignore
            self._db, self._raw_to_pit_in, query, params=tuple(params))
        return model

    def get_by_team_id(
            self,
            competition_id: int,
            team_id: int) -> List[GetPitIn]:
        """
        Retrieve a pit-in by its ID.

        Params:
            competition_id (int): ID of the competition.
            team_id (int): ID of the team.
            competition_id (int | None): If given, the pit-in must exist in the
                competition.

        Returns:
            List[GetPitIn]: List of pits-in in the competition and team.
        """
        query = f'''
            {self.BASE_QUERY}
            WHERE pin.competition_id = %s AND pin.team_id = %s'''
        params = [competition_id, team_id]
        models: List[GetPitIn] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_pit_in, query, params=tuple(params))
        return models

    def add_one(
            self,
            pit_in: AddPitIn,
            competition_id: int,
            commit: bool = True) -> int:
        """
        Add a new pit-in.

        Params:
            pit_in (AddPitIn): Data of the pit-in.
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.

        Returns:
            int: ID of inserted model.
        """
        model_data = pit_in.dict()
        model_data['competition_id'] = competition_id

        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=commit)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')
        return item_id

    def update_by_id(
            self,
            pit_in: TypeUpdatePitIn,
            pit_in_id: int,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the data of a pit-in (it must already exist).

        Params:
            pit_in (UpdatePitIn | ...): New data of the pit-in.
            pit_in_id (int): ID of the pit-in.
            competition_id (int | None): If given, the pit-in must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        previous_model = self.get_by_id(
            pit_in_id=pit_in_id, competition_id=competition_id)
        if previous_model is None:
            raise ApiError(
                message='The requested pit-in data does not exist.',
                status_code=400)
        update_model(
            self._db,
            self.TABLE_NAME,
            pit_in.dict(),
            key_name='id',
            key_value=pit_in_id,
            commit=commit)

    def _raw_to_pit_in(self, row: dict) -> GetPitIn:
        """Build an instance of GetPitIn."""
        return GetPitIn(
            id=row['pin_id'],
            competition_id=row['pin_competition_id'],
            team_id=row['pin_team_id'],
            driver_id=row['pin_driver_id'],
            lap=row['pin_lap'],
            pit_time=row['pin_pit_time'],
            kart_status=row['pin_kart_status'],
            fixed_kart_status=row['pin_fixed_kart_status'],
            insert_date=row['pin_insert_date'],
            update_date=row['pin_update_date'],
        )
