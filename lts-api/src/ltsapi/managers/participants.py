from logging import Logger
from typing import List, Optional, Tuple

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.models.filters import CodeFilter, IdFilter, NameFilter
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
            cd.`code` AS cd_code,
            cd.`name` AS cd_name,
            cd.`number` AS cd_number,
            cd.`total_driving_time` AS cd_total_driving_time,
            cd.`partial_driving_time` AS cd_partial_driving_time,
            cd.`reference_time_offset` AS cd_reference_time_offset,
            cd.`insert_date` AS cd_insert_date,
            cd.`update_date` AS cd_update_date
        FROM competitions_drivers AS cd'''
    BASE_INSERT = '''
        INSERT INTO `competitions_drivers`
        (
            `competition_id`, `team_id`, `code`, `name`, `number`,
            `total_driving_time`, `partial_driving_time`,
            `reference_time_offset`)
        VALUES'''
    BASE_UPDATE = 'UPDATE `competitions_drivers`'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetDriver]:
        """Get all drivers in the database."""
        return self._fetchmany_driver(self.BASE_QUERY)

    def get_by_id(self, filter: IdFilter) -> Optional[GetDriver]:
        """Retrieve a driver by its ID."""
        query = f'{self.BASE_QUERY} WHERE cd.id = %s'
        return self._fetchone_driver(query, (filter.id,))

    def get_by_competition_id(self, filter: IdFilter) -> List[GetDriver]:
        """Retrieve the drivers in a competition."""
        query = f'{self.BASE_QUERY} WHERE cd.competition_id = %s'
        return self._fetchmany_driver(query, (filter.id,))

    def get_by_team_id(self, filter: IdFilter) -> List[GetDriver]:
        """Retrieve the drivers in a team."""
        query = f'{self.BASE_QUERY} WHERE cd.team_id = %s'
        return self._fetchmany_driver(query, (filter.id,))

    def get_by_name_and_competition(
            self,
            filter_name: NameFilter,
            filter_competition: IdFilter) -> Optional[GetDriver]:
        """Retrieve a driver by its name and the competition ID."""
        query = f'''{self.BASE_QUERY} WHERE
                    cd.name = %s AND cd.competition_id = %s'''
        return self._fetchone_driver(
            query, (filter_name.name, filter_competition.id))

    def add_one(self, driver: AddDriver, commit: bool = True) -> None:
        """Add a new driver."""
        if self.exists_by_name(driver.team_id, driver.name):
            raise ApiError(
                message=f'The driver "{driver.name}" '
                        f'(team={driver.team_id}) already exists.',
                status_code=400)

        stmt = f'{self.BASE_INSERT} (%s, %s, %s, %s, %s, %s, %s, %s)'
        params = (
            driver.competition_id,
            driver.team_id,
            driver.code,
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
            self, driver: UpdateDriver, commit: bool = True) -> None:
        """Update the data of a driver."""
        if self.get_by_id(IdFilter(id=driver.id)) is None:
            raise ApiError(
                message=f'The driver with ID={driver.id} does not exist.',
                status_code=400)

        stmt, params = self._build_update(self.BASE_UPDATE, driver, key='id')
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def exists_by_name(
            self, team_id: Optional[int], driver_name: str) -> bool:
        """Check if a driver with the given code exists."""
        query = f'''
            {self.BASE_QUERY}
            WHERE cd.team_id = %s AND cd.name = %s'''
        matches = self._fetchmany_driver(query, (team_id, driver_name))
        return len(matches) > 0

    def _build_update(
            self,
            base_stmt: str,
            driver: UpdateDriver,
            key: str) -> Tuple[str, list]:
        """Build the statement to update a driver."""
        fields = {k: v for k, v in driver.dict(exclude={key}).items()
                  if v is not None}
        stmt_fields, params = list(fields.keys()), list(fields.values())
        stmt_fields = [f'`{field}` = %s' for field in stmt_fields]

        stmt = (f'{base_stmt} SET {",".join(stmt_fields)} '
                f'WHERE `{key}` = %s')
        params.append(driver.dict(include={key})[key])
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
            code=row['cd_code'],
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
            ct.`code` AS ct_code,
            ct.`name` AS ct_name,
            ct.`number` AS ct_number,
            ct.`reference_time_offset` AS ct_reference_time_offset,
            ct.`insert_date` AS ct_insert_date,
            ct.`update_date` AS ct_update_date
        FROM competitions_teams AS ct'''
    BASE_INSERT = '''
        INSERT INTO `competitions_teams`
        (`competition_id`, `code`, `name`, `number`, `reference_time_offset`)
        VALUES'''
    BASE_UPDATE = 'UPDATE `competitions_teams`'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetTeam]:
        """Get all teams in the database."""
        return self._fetchmany_team(self.BASE_QUERY)

    def get_by_id(self, filter: IdFilter) -> Optional[GetTeam]:
        """Retrieve a team by its ID."""
        query = f'{self.BASE_QUERY} WHERE ct.id = %s'
        return self._fetchone_team(query, (filter.id,))

    def get_by_competition_id(self, filter: IdFilter) -> List[GetTeam]:
        """Retrieve the teams in a competition."""
        query = f'{self.BASE_QUERY} WHERE ct.competition_id = %s'
        return self._fetchmany_team(query, (filter.id,))

    def get_by_code_and_competition(
            self,
            filter_code: CodeFilter,
            filter_competition: IdFilter) -> Optional[GetTeam]:
        """Retrieve a team by its code and the competition ID."""
        query = f'''{self.BASE_QUERY} WHERE
                    ct.code = %s AND ct.competition_id = %s'''
        return self._fetchone_team(
            query, (filter_code.code, filter_competition.id))

    def add_one(self, team: AddTeam, commit: bool = True) -> None:
        """Add a new team."""
        if self.exists_by_code(team.competition_id, team.code):
            raise ApiError(
                message=f'The team "{team.code}" '
                        f'(competition={team.competition_id}) already exists.',
                status_code=400)

        stmt = f'{self.BASE_INSERT} (%s, %s, %s, %s, %s)'
        params = (
            team.competition_id,
            team.code,
            team.name,
            team.number,
            team.reference_time_offset)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def update_by_id(
            self, team: UpdateTeam, commit: bool = True) -> None:
        """Update the data of a team."""
        if self.get_by_id(IdFilter(id=team.id)) is None:
            raise ApiError(
                message=f'The team with ID={team.id} does not exist.',
                status_code=400)

        stmt, params = self._build_update(self.BASE_UPDATE, team, key='id')
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def exists_by_code(
            self, competition_id: int, team_code: Optional[str]) -> bool:
        """Check if a team with the given code exists."""
        query = f'''
            {self.BASE_QUERY}
            WHERE ct.competition_id = %s AND ct.code = %s'''
        matches = self._fetchmany_team(query, (competition_id, team_code))
        return len(matches) > 0

    def _build_update(
            self,
            base_stmt: str,
            team: UpdateTeam,
            key: str) -> Tuple[str, list]:
        """Build the statement to update a team."""
        fields = {k: v for k, v in team.dict(exclude={key}).items()
                  if v is not None}
        stmt_fields, params = list(fields.keys()), list(fields.values())
        stmt_fields = [f'`{field}` = %s' for field in stmt_fields]

        stmt = (f'{base_stmt} SET {",".join(stmt_fields)} '
                f'WHERE `{key}` = %s')
        params.append(team.dict(include={key})[key])
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
            code=row['ct_code'],
            name=row['ct_name'],
            number=row['ct_number'],
            reference_time_offset=row['ct_reference_time_offset'],
            drivers=[],
            insert_date=row['ct_insert_date'],
            update_date=row['ct_update_date'],
        )
