from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.models.filters import IdFilter
from ltsapi.models.participants import AddTeam, GetTeam


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
    INSERT_STMT = '''
        INSERT INTO `competitions_teams`
        (`competition_id`, `code`, `name`, `number`, `reference_time_offset`)
        VALUES'''

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
        """Retrieve a team by its competition ID."""
        query = f'{self.BASE_QUERY} WHERE ct.competition_id = %s'
        return self._fetchmany_team(query, (filter.id,))

    def add_one(self, team: AddTeam, commit: bool = True) -> None:
        """Add a new team."""
        if self.exists_by_code(team.competition_id, team.code):
            raise ApiError(
                f'The team "{team.code}" '
                f'(competition = {team.competition_id}) already exists.')

        stmt = f'{self.INSERT_STMT} (%s, %s, %s, %s, %s)'
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

    def exists_by_code(
            self, competition_id: int, team_code: Optional[str]) -> bool:
        """Check if a team with the given code exists."""
        query = f'''
            {self.BASE_QUERY}
            WHERE ct.competition_id = %s AND ct.code = %s'''
        matches = self._fetchmany_team(query, (competition_id, team_code))
        return len(matches) > 0

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
