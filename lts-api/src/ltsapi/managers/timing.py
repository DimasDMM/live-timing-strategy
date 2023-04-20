from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    fetchmany_models,
    fetchone_model,
    insert_model,
    update_model,
)
from ltsapi.models.timing import (
    GetLapTime,
    UpdateLapTime,
)


class TimingManager:
    """Manage data of times."""

    BASE_SELECT = '''
        SELECT
            timing.`team_id` AS timing_team_id,
            timing.`driver_id` AS timing_driver_id,
            timing.`position` AS timing_position,
            timing.`time` AS timing_time,
            timing.`best_time` AS timing_best_time,
            timing.`lap` AS timing_lap,
            timing.`interval` AS timing_interval,
            timing.`interval_unit` AS timing_interval_unit,
            timing.`stage` AS timing_stage,
            timing.`pit_time` AS timing_pit_time,
            timing.`kart_status` AS timing_kart_status,
            timing.`fixed_kart_status` AS timing_fixed_kart_status,
            timing.`number_pits` AS timing_number_pits,
            timing.`insert_date` AS timing_insert_date,
            timing.`update_date` AS timing_update_date'''
    CURRENT_QUERY = f'{BASE_SELECT} FROM timing_current as timing'
    HISTORY_QUERY = f'{BASE_SELECT} FROM timing_history as timing'
    CURRENT_TABLE = 'timing_current'
    HISTORY_TABLE = 'timing_history'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_current_all_by_id(self, competition_id: int) -> List[GetLapTime]:
        """
        Retrieve the current timing of a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetLapTime]: List of all lap times of the
                competition of all participants.
        """
        query = f'{self.CURRENT_QUERY} WHERE timing.competition_id = %s'
        models: List[GetLapTime] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_timing, query, (competition_id,))
        return models

    def get_current_single_by_id(
            self,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None) -> Optional[GetLapTime]:
        """
        Retrieve the current timing of a specific participant.

        This method must receive the team ID and/or the driver ID.

        Params:
            competition_id (int): ID of the competition.
            team_id (int | None): If given, it filters by the timing of the
                given team.
            driver_id (int | None): If given, it filters by the timing of the
                given driver.

        Returns:
            Optional[GetLapTime]: Lap times of the competition of
                given participant.
        """
        if team_id is None and driver_id is None:
            raise ApiError('It is necessary to provide the ID of the team'
                           'and/or the ID of the driver.')

        query = f'{self.CURRENT_QUERY} WHERE timing.competition_id = %s'
        params = [competition_id]
        if team_id is not None:
            query = f'{query} AND timing.team_id = %s'
            params.append(team_id)
        if driver_id is not None:
            query = f'{query} AND timing.driver_id = %s'
            params.append(driver_id)
        model: Optional[GetLapTime] = fetchone_model(  # type: ignore
            self._db, self._raw_to_timing, query, tuple(params))
        return model

    def get_history_by_id(
            self,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None) -> List[GetLapTime]:
        """
        Retrieve the timing history of a competition.

        Params:
            competition_id (int): ID of the competition.
            team_id (int | None): If given, it filters by the history of the
                given team.
            driver_id (int | None): If given, it filters by the history of the
                given driver.

        Returns:
            List[GetLapTime]: History of all lap times of the
                competition.
        """
        query = f'{self.HISTORY_QUERY} WHERE timing.competition_id = %s'
        params = [competition_id]
        if team_id is not None:
            query = f'{query} AND timing.team_id = %s'
            params.append(team_id)
        if driver_id is not None:
            query = f'{query} AND timing.driver_id = %s'
            params.append(driver_id)
        models: List[GetLapTime] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_timing, query, tuple(params))
        return models

    def update_by_id(
            self,
            lap_time: UpdateLapTime,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the timing of a competition (it must already exist).

        Note that, after the record is updated, it also inserts a new row in the
        history table.

        Params:
            lap_time (UpdateLapTime): New timing data of the
                competition ('None' is ignored).
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.
        """
        previous_model = self.get_current_single_by_id(
            competition_id=competition_id, team_id=team_id, driver_id=driver_id)
        if previous_model is None:
            raise ApiError(
                message=('The requested timing data does not exist.'),
                status_code=400)

        key_name = ['competition_id']
        key_value = [competition_id]
        if team_id is not None:
            key_name.append('team_id')
            key_value.append(team_id)
        if driver_id is not None:
            key_name.append('driver_id')
            key_value.append(driver_id)
        update_model(
            self._db,
            self.CURRENT_TABLE,
            lap_time.dict(),
            key_name=key_name,
            key_value=key_value,
            commit=False)

        # Register new data in the history
        self._insert_history(
            competition_id=competition_id,
            previous_model=previous_model,
            new_model=lap_time,
            commit=commit)

    def _insert_history(
            self,
            competition_id: int,
            previous_model: GetLapTime,
            new_model: UpdateLapTime,
            commit: bool = True) -> None:
        """Insert record in the history table."""
        new_data = new_model.dict()
        previous_data = previous_model.dict(exclude={
            'insert_date': True, 'update_date': True})
        for field_name, _ in previous_data.items():
            if field_name in new_data and new_data[field_name] is not None:
                previous_data[field_name] = new_data[field_name]
        previous_data['competition_id'] = competition_id
        _ = insert_model(
            self._db,
            TimingManager.HISTORY_TABLE,
            previous_data,
            commit=commit)

    def _raw_to_timing(self, row: dict) -> GetLapTime:
        """Build an instance of GetLapTime."""
        return GetLapTime(
            team_id=row['timing_team_id'],
            driver_id=row['timing_driver_id'],
            position=row['timing_position'],
            time=row['timing_time'],
            best_time=row['timing_best_time'],
            lap=row['timing_lap'],
            interval=row['timing_interval'],
            interval_unit=row['timing_interval_unit'],
            stage=row['timing_stage'],
            pit_time=row['timing_pit_time'],
            kart_status=row['timing_kart_status'],
            fixed_kart_status=row['timing_fixed_kart_status'],
            number_pits=row['timing_number_pits'],
            insert_date=row['timing_insert_date'],
            update_date=row['timing_update_date'],
        )
