from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.models.competitions import AddCompetition, GetCompetition


class CompetitionManager:
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
    BASE_INSERT = '''
        INSERT INTO `competitions_index`
        (`track_id`, `competition_code`, `name`, `description`) VALUES'''

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_all(self) -> List[GetCompetition]:
        """Get all competitions in the database."""
        with self._db as cursor:
            cursor.execute(self.BASE_QUERY)
            raw_data: List[dict] = cursor.fetchall()  # type: ignore
            items: List[GetCompetition] = []
            for row in raw_data:
                items.append(self._raw_to_competition(row))  # type: ignore
            return items

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
        return self._fetchone_competition(query, (competition_id,))

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
        return self._fetchone_competition(query, (competition_code,))

    def add_one(self, competition: AddCompetition, commit: bool = True) -> None:
        """
        Add a new competition.

        Params:
            competition (AddCompetition): Data of the competition.
            commit (bool): Commit transaction.
        """
        code = competition.competition_code
        if self.get_by_code(code) is not None:
            raise ApiError(
                message=(
                    f'There is already a competition with the code "{code}".'),
                status_code=400)

        stmt = f'{self.BASE_INSERT} (%s, %s, %s, %s)'
        params = (
            competition.track_id,
            competition.competition_code,
            competition.name,
            competition.description)
        with self._db as cursor:
            cursor.execute(stmt, params)
            if commit:
                self._db.commit()

    def _fetchone_competition(
            self,
            query: str,
            params: Optional[tuple] = None) -> Optional[GetCompetition]:
        """Run the given query and retrieve a GetCompetition."""
        with self._db as cursor:
            cursor.execute(query, params)  # type: ignore
            raw_data: dict = cursor.fetchone()  # type: ignore
            return self._raw_to_competition(raw_data)

    def _raw_to_competition(
            self, row: Optional[dict]) -> Optional[GetCompetition]:
        """Build an instance of GetCompetition."""
        if row is None:
            return None
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
