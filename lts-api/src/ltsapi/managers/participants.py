from logging import Logger
from typing import Any, List, Optional, Tuple

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.models.participants import (
    AddDriver,
    AddTeam,
    GetDriver,
    GetTeam,
    UpdateDriver,
    UpdateTeam,
)


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
            cd.`reference_time_offset` AS cd_reference_time_offset,
            cd.`insert_date` AS cd_insert_date,
            cd.`update_date` AS cd_update_date
        FROM drivers AS cd'''
    BASE_INSERT = '''
        INSERT INTO `drivers`
        (
            `competition_id`, `team_id`, `participant_code`, `name`, `number`,
            `total_driving_time`, `partial_driving_time`,
            `reference_time_offset`)
        VALUES'''
    BASE_UPDATE = 'UPDATE `drivers`'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetDriver]:
        """Get all drivers in the database."""
        return self._fetchmany_driver(self.BASE_QUERY)

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
        return self._fetchone_driver(query, tuple(params))

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
        return self._fetchmany_driver(query, (competition_id,))

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
        return self._fetchmany_driver(query, tuple(params))

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
        return self._fetchone_driver(
            query, tuple(params))

    def add_one(
            self,
            driver: AddDriver,
            competition_id: int,
            team_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Add a new driver.

        Params:
            driver (AddDriver): Data of the driver.
            competition_id (int): ID of the competition.
            team_id (int | None): If given, the driver will be inserted in the
                given team.
            commit (bool): Commit transaction.
        """
        if self._exists_by_name(driver.name, team_id, competition_id):
            raise ApiError(
                message=f'The driver "{driver.name}" '
                        f'(team={team_id}) already exists.',
                status_code=400)

        stmt = f'{self.BASE_INSERT} (%s, %s, %s, %s, %s, %s, %s, %s)'
        params = (
            competition_id,
            team_id,
            driver.participant_code,
            driver.name,
            driver.number,
            driver.total_driving_time,
            driver.partial_driving_time,
            driver.reference_time_offset)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

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
            driver (UpdateDriver): New data of the driver ('None' is ignored).
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

        stmt, params = self._build_update(
            self.BASE_UPDATE, driver, key_name='id', key_value=driver_id)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

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

        matches = self._fetchmany_driver(query, tuple(params))
        return len(matches) > 0

    def _build_update(
            self,
            base_stmt: str,
            driver: UpdateDriver,
            key_name: str,
            key_value: int) -> Tuple[str, list]:
        """Build the statement to update a driver."""
        fields = {k: v for k, v in driver.dict().items()
                  if v is not None}
        stmt_fields, params = list(fields.keys()), list(fields.values())
        stmt_fields = [f'`{field}` = %s' for field in stmt_fields]

        stmt = (f'{base_stmt} SET {",".join(stmt_fields)} '
                f'WHERE `{key_name}` = %s')
        params.append(key_value)
        return stmt, params

    def _fetchone_driver(
            self,
            query: str,
            params: Optional[tuple] = None) -> Optional[GetDriver]:
        """Run the given query and retrieve a single GetDriver."""
        with self._db as cursor:
            cursor.execute(query, params)  # type: ignore
            raw_data: dict = cursor.fetchone()  # type: ignore
            return self._raw_to_driver(raw_data)

    def _fetchmany_driver(
            self,
            query: str,
            params: Optional[tuple] = None) -> List[GetDriver]:
        """Run the given query and retrieve many GetDriver."""
        with self._db as cursor:
            cursor.execute(query, params)
            raw_data: List[dict] = cursor.fetchall()  # type: ignore
            items: List[GetDriver] = []
            for row in raw_data:
                items.append(self._raw_to_driver(row))  # type: ignore
            return items

    def _raw_to_driver(
            self, row: Optional[dict]) -> Optional[GetDriver]:
        """Build an instance of GetDriver."""
        if row is None:
            return None
        return GetDriver(
            id=row['cd_id'],
            competition_id=row['cd_competition_id'],
            team_id=row['cd_team_id'],
            participant_code=row['cd_participant_code'],
            name=row['cd_name'],
            number=row['cd_number'],
            total_driving_time=row['cd_total_driving_time'],
            partial_driving_time=row['cd_partial_driving_time'],
            reference_time_offset=row['cd_reference_time_offset'],
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
            ct.`reference_time_offset` AS ct_reference_time_offset,
            ct.`insert_date` AS ct_insert_date,
            ct.`update_date` AS ct_update_date
        FROM teams AS ct'''
    BASE_INSERT = '''
        INSERT INTO `teams`
        (`competition_id`, `participant_code`, `name`,
        `number`, `reference_time_offset`) VALUES'''
    BASE_UPDATE = 'UPDATE `teams`'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetTeam]:
        """Get all teams in the database."""
        return self._fetchmany_team(self.BASE_QUERY)

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
        return self._fetchone_team(query, tuple(params))

    def get_by_competition_id(self, competition_id: int) -> List[GetTeam]:
        """
        Retrieve the teams in a competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetTeam]: List of teams in the competition.
        """
        query = f'{self.BASE_QUERY} WHERE ct.competition_id = %s'
        return self._fetchmany_team(query, (competition_id,))

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
        return self._fetchone_team(
            query, (participant_code, competition_id))

    def add_one(
            self,
            team: AddTeam,
            competition_id: int,
            commit: bool = True) -> None:
        """
        Add a new team.

        Params:
            team (AddTeam): Data of the team.
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.
        """
        if self._exists_by_code(competition_id, team.participant_code):
            raise ApiError(
                message=f'The team "{team.participant_code}" '
                        f'(competition={competition_id}) already exists.',
                status_code=400)

        stmt = f'{self.BASE_INSERT} (%s, %s, %s, %s, %s)'
        params = (
            competition_id,
            team.participant_code,
            team.name,
            team.number,
            team.reference_time_offset)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def update_by_id(
            self,
            team: UpdateTeam,
            team_id: int,
            competition_id: Optional[int] = None,
            commit: bool = True) -> None:
        """
        Update the data of a team.

        Params:
            team (UpdateTeam): New data of the team ('None' is ignored).
            team_id (int): ID of the team.
            competition_id (int | None): If given, the team must exist
                in the competition.
            commit (bool): Commit transaction.
        """
        if self.get_by_id(team_id, competition_id) is None:
            raise ApiError(
                message=f'The team with ID={team_id} does not exist.',
                status_code=400)

        stmt, params = self._build_update(
            self.BASE_UPDATE, team, key_name='id', key_value=team_id)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def _exists_by_code(
            self, competition_id: int, team_code: Optional[str]) -> bool:
        """Check if a team with the given code exists."""
        query = f'''
            {self.BASE_QUERY}
            WHERE ct.competition_id = %s AND ct.participant_code = %s'''
        matches = self._fetchmany_team(query, (competition_id, team_code))
        return len(matches) > 0

    def _build_update(
            self,
            base_stmt: str,
            team: UpdateTeam,
            key_name: str,
            key_value: int) -> Tuple[str, list]:
        """Build the statement to update a team."""
        fields = {k: v for k, v in team.dict().items()
                  if v is not None}
        stmt_fields, params = list(fields.keys()), list(fields.values())
        stmt_fields = [f'`{field}` = %s' for field in stmt_fields]

        stmt = (f'{base_stmt} SET {",".join(stmt_fields)} '
                f'WHERE `{key_name}` = %s')
        params.append(key_value)
        return stmt, params

    def _fetchone_team(
            self,
            query: str,
            params: Optional[tuple] = None) -> Optional[GetTeam]:
        """Run the given query and retrieve a single GetTeam."""
        with self._db as cursor:
            cursor.execute(query, params)  # type: ignore
            raw_data: dict = cursor.fetchone()  # type: ignore
            return self._raw_to_team(raw_data)

    def _fetchmany_team(
            self,
            query: str,
            params: Optional[tuple] = None) -> List[GetTeam]:
        """Run the given query and retrieve many GetTeam."""
        with self._db as cursor:
            cursor.execute(query, params)
            raw_data: List[dict] = cursor.fetchall()  # type: ignore
            items: List[GetTeam] = []
            for row in raw_data:
                items.append(self._raw_to_team(row))  # type: ignore
            return items

    def _raw_to_team(
            self, row: Optional[dict]) -> Optional[GetTeam]:
        """Build an instance of GetTeam."""
        if row is None:
            return None
        return GetTeam(
            id=row['ct_id'],
            competition_id=row['ct_competition_id'],
            participant_code=row['ct_participant_code'],
            name=row['ct_name'],
            number=row['ct_number'],
            reference_time_offset=row['ct_reference_time_offset'],
            drivers=[],
            insert_date=row['ct_insert_date'],
            update_date=row['ct_update_date'],
        )
