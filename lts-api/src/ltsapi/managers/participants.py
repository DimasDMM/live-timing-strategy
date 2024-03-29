from logging import Logger
from typing import Any, List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.timing import TimingManager
from ltsapi.managers.utils.statements import (
    insert_model,
    update_model,
    fetchmany_models,
    fetchone_model,
)
from ltsapi.models.enum import CompetitionStage, KartStatus
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
    GetDriver,
    GetTeam,
    UpdateDriver,
    UpdateTeam,
    UpdatePartialTimeDriver,
    UpdateTotalTimeDriver,
)
from ltsapi.models.timing import AddTiming


class DriversManager:
    """Manage data of drivers."""

    BASE_QUERY = '''
        SELECT
            cd.`id` AS cd_id,
            cd.`competition_id` AS cd_competition_id,
            cd.`team_id` AS cd_team_id,
            cd.`participant_code` AS cd_participant_code,
            cd.`name` AS cd_name,
            cd.`number` AS cd_number,
            cd.`total_driving_time` AS cd_total_driving_time,
            cd.`partial_driving_time` AS cd_partial_driving_time,
            cd.`insert_date` AS cd_insert_date,
            cd.`update_date` AS cd_update_date
        FROM participants_drivers AS cd'''
    TABLE_NAME = 'participants_drivers'

    def __init__(
            self,
            db: DBContext,
            logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetDriver]:
        """Get all drivers in the database."""
        models: List[GetDriver] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_driver, self.BASE_QUERY)
        return models

    def get_by_id(
            self,
            driver_id: int,
            team_id: Optional[int] = None,
            competition_id: Optional[int] = None) -> Optional[GetDriver]:
        """
        Retrieve a driver by its ID.

        Params:
            driver_id (int): ID of the driver.
            team_id (int | None): If given, the driver must exist in the team.
            competition_id (int | None): If given, the driver must exist in the
                competition.

        Returns:
            GetDriver | None: If the driver exists, it returns its instance.
        """
        query = f'{self.BASE_QUERY} WHERE cd.id = %s'
        params = [driver_id]
        if team_id is not None:
            query = f'{query} AND cd.team_id = %s'
            params.append(team_id)
        if competition_id is not None:
            query = f'{query} AND cd.competition_id = %s'
            params.append(competition_id)
        model: Optional[GetDriver] = fetchone_model(  # type: ignore
            self._db, self._raw_to_driver, query, params=tuple(params))
        return model

    def get_by_competition_id(
            self,
            competition_id: int) -> List[GetDriver]:
        """
        Retrieve the drivers in a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetDriver]: List of drivers in the competition.
        """
        query = f'{self.BASE_QUERY} WHERE cd.competition_id = %s'
        models: List[GetDriver] = fetchmany_models(  # type: ignore
            self._db,
            self._raw_to_driver,
            query,
            params=(competition_id,))
        return models

    def get_by_team_id(
            self,
            team_id: int,
            competition_id: Optional[int] = None) -> List[GetDriver]:
        """
        Retrieve the drivers in a team.

        Params:
            team_id (int): ID of the team.
            competition_id (int | None): If given, the team must exist in the
                competition.

        Returns:
            List[GetDriver]: List of drivers in the team.
        """
        query = f'{self.BASE_QUERY} WHERE cd.team_id = %s'
        params = [team_id]
        if competition_id is not None:
            query = f'{query} AND cd.competition_id = %s'
            params.append(competition_id)
        models: List[GetDriver] = fetchmany_models(  # type: ignore
            self._db,
            self._raw_to_driver,
            query,
            params=tuple(params))
        return models

    def get_by_name(
            self,
            driver_name: str,
            competition_id: int,
            team_id: Optional[int] = None) -> Optional[GetDriver]:
        """
        Retrieve a driver by its name.

        Params:
            driver_name (str): Name of the driver.
            competition_id (int): ID of the competition.
            team_id (int): If given, the driver must exist in the team.

        Returns:
            GetDriver | None: If the driver exists, it returns its instance.
        """
        query = f'''
            {self.BASE_QUERY} WHERE
            cd.name = %s AND cd.competition_id = %s'''
        params = [driver_name, competition_id]
        if competition_id is not None:
            query = f'{query} AND cd.team_id = %s'
            params.append(team_id)
        model: Optional[GetDriver] = fetchone_model(  # type: ignore
            self._db, self._raw_to_driver, query, params=tuple(params))
        return model

    def add_one(
            self,
            driver: AddDriver,
            competition_id: int,
            team_id: Optional[int] = None,
            commit: bool = True) -> int:
        """
        Add a new driver.

        Params:
            driver (AddDriver): Data of the driver.
            competition_id (int): ID of the competition.
            team_id (int | None): If given, the driver will be inserted in the
                given team.
            commit (bool): Commit transaction.

        Returns:
            int: ID of inserted model.
        """
        if self._exists_by_name(driver.name, team_id, competition_id):
            raise ApiError(
                message=f'The driver "{driver.name}" '
                        f'(team={team_id}) already exists.',
                status_code=400)

        model_data = driver.model_dump()
        model_data['competition_id'] = competition_id
        model_data['team_id'] = team_id
        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=False)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')

        # Additional information required when we create a new driver.
        # Note that this section is executed only if the driver does not have
        # any team (otherwise, it asumes that these records already exist
        # because they were created along the team).
        if team_id is None:
            initial_model = self._initial_timing(driver_id=item_id)
            initial_data = initial_model.model_dump()
            initial_data['competition_id'] = competition_id
            _ = insert_model(
                self._db,
                TimingManager.CURRENT_TABLE,
                initial_data,
                commit=False)
            _ = insert_model(
                self._db,
                TimingManager.HISTORY_TABLE,
                initial_data,
                commit=False)

        if commit:
            try:
                self._db.commit()
            except Exception as e:
                self._db.rollback()
                raise e

        return item_id

    def update_by_id(
            self,
            driver: UpdateDriver,
            driver_id: int,
            team_id: Optional[int] = None,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the data of a driver (it must already exist).

        Params:
            driver (UpdateDriver): New data of the driver.
            driver_id (int): ID of the driver.
            team_id (int | None): If given, the driver must exist in the team.
            competition_id (int | None): If given, the driver must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        if self.get_by_id(driver_id, team_id, competition_id) is None:
            raise ApiError(
                message=f'The driver with ID={driver_id} does not exist.',
                status_code=400)
        update_model(
            self._db,
            self.TABLE_NAME,
            driver.model_dump(),
            key_name='id',
            key_value=driver_id,
            commit=commit)

    def update_partial_driving_time_by_id(
            self,
            time: UpdatePartialTimeDriver,
            driver_id: int,
            team_id: Optional[int] = None,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the partial driving time of a driver (it must already exist).

        Note that, if time.auto_compute_total is True, then it computes the
        total driving time too.

        Params:
            time (UpdatePartialTimeDriver): Partial driving time of the driver.
            driver_id (int): ID of the driver.
            team_id (int | None): If given, the driver must exist in the team.
            competition_id (int | None): If given, the driver must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        item = self.get_by_id(driver_id, team_id, competition_id)
        if item is None:
            raise ApiError(
                message=f'The driver with ID={driver_id} does not exist.',
                status_code=400)

        data = {'partial_driving_time': time.partial_driving_time}

        if (time.auto_compute_total
                and item.partial_driving_time < time.partial_driving_time):
            data['total_driving_time'] = (
                item.total_driving_time + time.partial_driving_time)

        update_model(
            self._db,
            self.TABLE_NAME,
            data,
            key_name='id',
            key_value=driver_id,
            commit=commit)

    def update_total_driving_time_by_id(
            self,
            time: UpdateTotalTimeDriver,
            driver_id: int,
            team_id: Optional[int] = None,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the total driving time of a driver (it must already exist).

        Params:
            time (UpdateTotalTimeDriver): Total driving time of the driver.
            driver_id (int): ID of the driver.
            team_id (int | None): If given, the driver must exist in the team.
            competition_id (int | None): If given, the driver must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        item = self.get_by_id(driver_id, team_id, competition_id)
        if item is None:
            raise ApiError(
                message=f'The driver with ID={driver_id} does not exist.',
                status_code=400)

        data = {'total_driving_time': time.total_driving_time}
        update_model(
            self._db,
            self.TABLE_NAME,
            data,
            key_name='id',
            key_value=driver_id,
            commit=commit)

    def _exists_by_name(
            self,
            driver_name: str,
            team_id: Optional[int],
            competition_id: Optional[int]) -> bool:
        """Check if a driver with the given code exists."""
        query = f'{self.BASE_QUERY} WHERE cd.name = %s'
        params: List[Any] = [driver_name]

        if team_id is not None:
            query = f'{query} AND cd.team_id = %s'
            params.append(team_id)
        if competition_id is not None:
            query = f'{query} AND cd.competition_id = %s'
            params.append(competition_id)

        models: List[GetDriver] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_driver, query, params=tuple(params))
        return len(models) > 0

    def _initial_timing(self, driver_id: int) -> AddTiming:
        """Create initial timing data."""
        return AddTiming(
            team_id=None,
            driver_id=driver_id,
            position=0,
            last_time=0,
            best_time=0,
            lap=0,
            gap=None,
            gap_unit=None,
            interval=None,
            interval_unit=None,
            stage=CompetitionStage.FREE_PRACTICE,
            pit_time=0,
            kart_status=KartStatus.UNKNOWN,
            fixed_kart_status=None,
            number_pits=0,
        )

    def _raw_to_driver(self, row: dict) -> GetDriver:
        """Build an instance of GetDriver."""
        return GetDriver(
            id=row['cd_id'],
            competition_id=row['cd_competition_id'],
            team_id=row['cd_team_id'],
            participant_code=row['cd_participant_code'],
            name=row['cd_name'],
            number=row['cd_number'],
            total_driving_time=row['cd_total_driving_time'],
            partial_driving_time=row['cd_partial_driving_time'],
            insert_date=row['cd_insert_date'],
            update_date=row['cd_update_date'],
        )


class TeamsManager:
    """Manage data of teams."""

    BASE_QUERY = '''
        SELECT
            ct.`id` AS ct_id,
            ct.`competition_id` AS ct_competition_id,
            ct.`participant_code` AS ct_participant_code,
            ct.`name` AS ct_name,
            ct.`number` AS ct_number,
            ct.`insert_date` AS ct_insert_date,
            ct.`update_date` AS ct_update_date
        FROM participants_teams AS ct'''
    TABLE_NAME = 'participants_teams'

    def __init__(
            self,
            db: DBContext,
            logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetTeam]:
        """Get all teams in the database."""
        models: List[GetTeam] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_team, self.BASE_QUERY)
        return models

    def get_by_id(
            self,
            team_id: int,
            competition_id: Optional[int] = None) -> Optional[GetTeam]:
        """
        Retrieve a team by its ID.

        Params:
            team_id (int): ID of the team.
            competition_id (int | None): If given, the team must exist in the
                competition.

        Returns:
            GetTeam | None: If the team exists, it returns its instance.
        """
        query = f'{self.BASE_QUERY} WHERE ct.id = %s'
        params = [team_id]
        if competition_id is not None:
            query = f'{query} AND ct.competition_id = %s'
            params.append(competition_id)
        model: Optional[GetTeam] = fetchone_model(  # type: ignore
            self._db, self._raw_to_team, query, params=tuple(params))
        return model

    def get_by_competition_id(self, competition_id: int) -> List[GetTeam]:
        """
        Retrieve the teams in a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetTeam]: List of teams in the competition.
        """
        query = f'{self.BASE_QUERY} WHERE ct.competition_id = %s'
        models: List[GetTeam] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_team, query, params=(competition_id,))
        return models

    def get_by_code(
            self,
            participant_code: str,
            competition_id: int) -> Optional[GetTeam]:
        """
        Retrieve a team by its code and the competition ID.

        Params:
            participant_code (str): Code of the team.
            competition_id (int): ID of the competition.

        Returns:
            GetTeam | None: If the team exist, it returns its instance.
        """
        query = f'''{self.BASE_QUERY} WHERE
                    ct.participant_code = %s AND ct.competition_id = %s'''
        params = (participant_code, competition_id)
        model: Optional[GetTeam] = fetchone_model(  # type: ignore
            self._db, self._raw_to_team, query, params=tuple(params))
        return model

    def add_one(
            self,
            team: AddTeam,
            competition_id: int,
            commit: bool = True) -> int:
        """
        Add a new team.

        Params:
            team (AddTeam): Data of the team.
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.

        Returns:
            int: ID of inserted model.
        """
        if self._exists_by_code(competition_id, team.participant_code):
            raise ApiError(
                message=f'The team "{team.participant_code}" '
                        f'(competition={competition_id}) already exists.',
                status_code=400)

        model_data = team.model_dump()
        model_data['competition_id'] = competition_id
        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=False)
        if item_id is None:
            raise ApiError('No data was inserted or updated.')

        # Additional information required when we create a new team.
        initial_model = self._initial_timing(team_id=item_id)
        initial_data = initial_model.model_dump()
        initial_data['competition_id'] = competition_id
        _ = insert_model(
            self._db,
            TimingManager.CURRENT_TABLE,
            initial_data,
            commit=False)
        _ = insert_model(
            self._db,
            TimingManager.HISTORY_TABLE,
            initial_data,
            commit=commit)

        return item_id

    def update_by_id(
            self,
            team: UpdateTeam,
            team_id: int,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the data of a team.

        Params:
            team (UpdateTeam): New data of the team.
            team_id (int): ID of the team.
            competition_id (int | None): If given, the team must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        if self.get_by_id(team_id, competition_id) is None:
            raise ApiError(
                message=f'The team with ID={team_id} does not exist.',
                status_code=400)
        update_model(
            self._db,
            self.TABLE_NAME,
            team.model_dump(),
            key_name='id',
            key_value=team_id,
            commit=commit)

    def _exists_by_code(
            self, competition_id: int, team_code: Optional[str]) -> bool:
        """Check if a team with the given code exists."""
        query = f'''
            {self.BASE_QUERY}
            WHERE ct.competition_id = %s AND ct.participant_code = %s'''
        params = (competition_id, team_code)
        models: List[GetTeam] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_team, query, params)
        return len(models) > 0

    def _initial_timing(self, team_id: int) -> AddTiming:
        """Create initial timing data."""
        return AddTiming(
            team_id=team_id,
            driver_id=None,
            position=0,
            last_time=0,
            best_time=0,
            lap=0,
            gap=None,
            gap_unit=None,
            interval=None,
            interval_unit=None,
            stage=CompetitionStage.FREE_PRACTICE,
            pit_time=0,
            kart_status=KartStatus.UNKNOWN,
            fixed_kart_status=None,
            number_pits=0,
        )

    def _raw_to_team(self, row: dict) -> GetTeam:
        """Build an instance of GetTeam."""
        return GetTeam(
            id=row['ct_id'],
            competition_id=row['ct_competition_id'],
            participant_code=row['ct_participant_code'],
            name=row['ct_name'],
            number=row['ct_number'],
            insert_date=row['ct_insert_date'],
            update_date=row['ct_update_date'],
        )
