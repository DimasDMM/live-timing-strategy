from copy import deepcopy
from logging import Logger
from typing import List, Optional, Union

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    fetchmany_models,
    fetchone_model,
    insert_model,
    update_model,
)
from ltsapi.models import BaseModel
from ltsapi.models.timing import (
    GetTiming,
    UpdateTiming,
    UpdateTimingDriver,
    UpdateTimingPosition,
    UpdateTimingLastTime,
    UpdateTimingLastTimeWBest,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingGap,
    UpdateTimingInterval,
    UpdateTimingStage,
    UpdateTimingPitTime,
    UpdateTimingKartStatus,
    UpdateTimingFixedKartStatus,
    UpdateTimingNumberPits,
)

# Alias of all fields that we may update in timing
TypeUpdateTiming = Union[
    UpdateTiming,
    UpdateTimingDriver,
    UpdateTimingPosition,
    UpdateTimingLastTime,
    UpdateTimingLastTimeWBest,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingGap,
    UpdateTimingInterval,
    UpdateTimingStage,
    UpdateTimingPitTime,
    UpdateTimingKartStatus,
    UpdateTimingFixedKartStatus,
    UpdateTimingNumberPits,
]

# Alias to update the last time and, maybe, the best time too
TypeUpdateTimingLastTime = Union[
    UpdateTiming,
    UpdateTimingLastTime,
    UpdateTimingLastTimeWBest,
]


class TimingManager:
    """Manage data of times."""

    BASE_SELECT = '''
        SELECT
            drivers.`participant_code` AS driver_code,
            teams.`participant_code` AS team_code,
            timing.`team_id` AS timing_team_id,
            timing.`driver_id` AS timing_driver_id,
            timing.`position` AS timing_position,
            timing.`last_time` AS timing_last_time,
            timing.`best_time` AS timing_best_time,
            timing.`lap` AS timing_lap,
            timing.`gap` AS timing_gap,
            timing.`gap_unit` AS timing_gap_unit,
            timing.`interval` AS timing_interval,
            timing.`interval_unit` AS timing_interval_unit,
            timing.`stage` AS timing_stage,
            timing.`pit_time` AS timing_pit_time,
            timing.`kart_status` AS timing_kart_status,
            timing.`fixed_kart_status` AS timing_fixed_kart_status,
            timing.`number_pits` AS timing_number_pits,
            timing.`insert_date` AS timing_insert_date,
            timing.`update_date` AS timing_update_date'''
    CURRENT_QUERY = f'''
        {BASE_SELECT} FROM timing_current AS timing
        LEFT JOIN participants_drivers AS drivers
            ON drivers.id = timing.`driver_id`
        LEFT JOIN participants_teams AS teams
            ON teams.id = timing.`team_id`
    '''
    HISTORY_QUERY = f'''
        {BASE_SELECT} FROM timing_history AS timing
        LEFT JOIN participants_drivers AS drivers
            ON drivers.id = timing.`driver_id`
        LEFT JOIN participants_teams AS teams
            ON teams.id = timing.`team_id`
    '''
    CURRENT_TABLE = 'timing_current'
    HISTORY_TABLE = 'timing_history'

    # Fields that the model might have and they should be exluded when we run
    # an update or insert statement
    EXCLUDE_ON_UPDATE = {
        'auto_best_time': True,
        'auto_other_positions': True,
        'participant_code': True,
        'insert_date': True,
        'update_date': True,
    }

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_current_all_by_id(self, competition_id: int) -> List[GetTiming]:
        """
        Retrieve the current timing of a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetTiming]: List of all lap times of the
                competition of all participants.
        """
        query = f'{self.CURRENT_QUERY} WHERE timing.competition_id = %s'
        models: List[GetTiming] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_timing, query, (competition_id,))
        return models

    def get_current_single_by_id(
            self,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None) -> Optional[GetTiming]:
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
            Optional[GetTiming]: Timing of the competition of
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
        model: Optional[GetTiming] = fetchone_model(  # type: ignore
            self._db, self._raw_to_timing, query, tuple(params))
        return model

    def get_history_by_id(
            self,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None) -> List[GetTiming]:
        """
        Retrieve the timing history of a competition.

        Params:
            competition_id (int): ID of the competition.
            team_id (int | None): If given, it filters by the history of the
                given team.
            driver_id (int | None): If given, it filters by the history of the
                given driver.

        Returns:
            List[GetTiming]: History of all lap times of the
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
        models: List[GetTiming] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_timing, query, tuple(params))
        return models

    def get_current_between_positions(
            self,
            competition_id: int,
            start_position: int,
            end_position: int) -> List[GetTiming]:
        """
        Retrieve the timing of participants between the given positions.

        The timing items that retrieves are in the range [start, end], that is,
        start and end are included.

        Params:
            competition_id (int): ID of the competition.
            start_position (int): Start position to filter.
            end_position (int): End position to filter.

        Returns:
            List[GetTiming]: Timing of the competition of participants in the
                specified range of positions.
        """
        query = f'''
            {self.CURRENT_QUERY}
            WHERE timing.competition_id = %s
                AND timing.position >= %s
                AND timing.position <= %s'''
        params = (competition_id, start_position, end_position)
        models: List[GetTiming] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_timing, query, params)
        return models

    def update_by_id(
            self,
            timing: TypeUpdateTiming,
            competition_id: int,
            team_id: Optional[int] = None,
            driver_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the timing of a competition (it must already exist).

        Note that, after the record is updated, it also inserts a new row in the
        history table.

        Params:
            timing (UpdateTiming | ...): New timing data of the
                competition ('None' is ignored).
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.
        """
        previous_model = self.get_current_single_by_id(
            competition_id=competition_id, team_id=team_id, driver_id=driver_id)
        if previous_model is None:
            raise ApiError(
                message='The requested timing data does not exist.',
                status_code=400)

        # If the position is modified, change other participant's positions too
        if (isinstance(timing, (UpdateTiming, UpdateTimingPosition))):
            self.__update_other_positions(
                competition_id,
                new_model=timing,
                previous_model=previous_model)

        # Update best time if given
        if (isinstance(timing, (UpdateTiming, UpdateTimingLastTime))):
            timing = self.__override_best_time(  # type: ignore
                timing, previous_model)

        key_name, key_value = self.__prepare_key_for_update(
            competition_id, team_id, driver_id)
        update_model(
            self._db,
            self.CURRENT_TABLE,
            timing.dict(exclude=self.EXCLUDE_ON_UPDATE),
            key_name=key_name,
            key_value=key_value,
            commit=False)

        # Register new data in the history
        self._insert_history(
            competition_id=competition_id,
            previous_model=previous_model,
            new_model=timing,
            commit=commit)

    def __update_other_positions(
            self,
            competition_id: int,
            new_model: Union[UpdateTiming, UpdateTimingPosition],
            previous_model: GetTiming) -> None:
        """
        Update the position of other participants.

        When the position of a driver changes, the position of the other
        participants should change too.
        """
        if (not new_model.auto_other_positions
                or new_model.position == previous_model.position):
            # No need to update positions
            return
        elif new_model.position > previous_model.position:
            # The participant is behind
            start_position = previous_model.position + 1
            end_position = new_model.position
            order = -1
        else:
            # The participant is in the front
            start_position = new_model.position
            end_position = previous_model.position - 1
            order = 1

        other_participants = self.get_current_between_positions(
            competition_id, start_position, end_position)
        for p in other_participants:
            previous_p = deepcopy(p)
            p.position += order
            key_name, key_value = self.__prepare_key_for_update(
                competition_id, p.team_id, p.driver_id)
            update_model(
                self._db,
                self.CURRENT_TABLE,
                p.dict(exclude=self.EXCLUDE_ON_UPDATE),
                key_name=key_name,
                key_value=key_value,
                commit=False)
            self._insert_history(
                competition_id,
                previous_model=previous_p,
                new_model=p.to_adder(),
                commit=False)

    def __override_best_time(
            self,
            timing: Union[UpdateTiming, UpdateTimingLastTime],
            previous_model: GetTiming) -> TypeUpdateTimingLastTime:
        """Override best time field if the last time is better."""
        if not timing.auto_best_time:
            return timing
        elif previous_model.best_time > timing.last_time:
            return UpdateTimingLastTimeWBest(
                last_time=timing.last_time,
                best_time=timing.last_time,
            )
        else:
            return timing

    def _insert_history(
            self,
            competition_id: int,
            previous_model: GetTiming,
            new_model: BaseModel,
            commit: bool = True) -> None:
        """Insert record in the history table."""
        previous_data = previous_model.dict(exclude=self.EXCLUDE_ON_UPDATE)
        new_data = new_model.dict(exclude=self.EXCLUDE_ON_UPDATE)

        for field_name, _ in previous_data.items():
            if field_name in new_data:
                previous_data[field_name] = new_data[field_name]
        previous_data['competition_id'] = competition_id
        _ = insert_model(
            self._db,
            TimingManager.HISTORY_TABLE,
            previous_data,
            commit=commit)

    def _raw_to_timing(self, row: dict) -> GetTiming:
        """Build an instance of GetTiming."""
        participant_code = (row['team_code'] if row['team_code'] is not None
                            else row['driver_code'])
        return GetTiming(
            team_id=row['timing_team_id'],
            driver_id=row['timing_driver_id'],
            participant_code=participant_code,
            position=row['timing_position'],
            last_time=row['timing_last_time'],
            best_time=row['timing_best_time'],
            lap=row['timing_lap'],
            gap=row['timing_gap'],
            gap_unit=row['timing_gap_unit'],
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

    def __prepare_key_for_update(
            self,
            competition_id: int,
            team_id: Optional[int],
            driver_id: Optional[int]) -> tuple:
        """
        Prepare key to run update statement.

        This is an auxiliar method of update_by_id().
        """
        key_name = ['competition_id']
        key_value = [competition_id]
        if team_id is not None:
            key_name.append('team_id')
            key_value.append(team_id)
        if driver_id is not None:
            key_name.append('driver_id')
            key_value.append(driver_id)
        return (key_name, key_value)
