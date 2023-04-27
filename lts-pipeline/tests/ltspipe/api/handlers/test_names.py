import pytest
from typing import List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.handlers.names import (
    UpdateDriverHandler,
    UpdateTeamHandler,
)
from ltspipe.data.competitions import (
    CompetitionInfo,
    Driver,
    Team,
    UpdateDriver,
    UpdateTeam,
)
from tests.fixtures import AUTH_KEY, REAL_API_LTS
from tests.helpers import DatabaseTest


class TestUpdateDriverHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateDriverHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'update_data_1', 'update_data_2',
         'expected_drivers_1', 'expected_drivers_2'),
        [
            (
                'south-endurance-2023-03-26',  # competition_code
                UpdateDriver(  # update_data_1
                    id=None,
                    competition_code='south-endurance-2023-03-26',
                    participant_code='team-1',
                    name='CKM 1 Driver 3',
                    number=41,
                    team_id=6,
                ),
                UpdateDriver(  # update_data_2
                    id=None,
                    competition_code='south-endurance-2023-03-26',
                    participant_code='team-1',
                    name='CKM 1 Driver 3',
                    number=51,
                    team_id=6,
                ),
                [  # expected_drivers_1
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 1',
                        number=41,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 2',
                        number=41,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 3',
                        number=41,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
                [  # expected_drivers_2
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 1',
                        number=41,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 2',
                        number=41,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                    Driver(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1 Driver 3',
                        number=51,
                        team_id=6,
                        total_driving_time=0,
                        partial_driving_time=0,
                    ),
                ],
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data_1: UpdateDriver,
            update_data_2: UpdateDriver,
            expected_drivers_1: List[Driver],
            expected_drivers_2: List[Driver]) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateDriverHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        handler.handle(update_data_1)
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_1])

        # Second call to handle method
        handler = UpdateDriverHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        model = self._find_driver(info, update_data_2.name)
        update_data_2.id = model.id
        handler.handle(update_data_2)
        assert ([d.dict(exclude={'id': True}) for d in info.drivers]
                == [d.dict(exclude={'id': True}) for d in expected_drivers_2])

    def _find_driver(
            self,
            info: CompetitionInfo,
            driver_name: str) -> Driver:
        """Find a driver in the competition info."""
        for d in info.drivers:
            if d.name == driver_name:
                return d
        raise Exception(f'Driver "{driver_name}" not found')


class TestUpdateTeamHandler(DatabaseTest):
    """
    Functional test of ltspipe.api.handlers.UpdateTeamHandler.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    @pytest.mark.parametrize(
        ('competition_code', 'update_data_1', 'update_data_2',
         'expected_teams_1', 'expected_teams_2'),
        [
            (
                'north-endurance-2023-03-25',  # competition_code
                UpdateTeam(  # update_data_1
                    id=None,
                    competition_code='north-endurance-2023-03-25',
                    participant_code='team-3',
                    name='CKM 3',
                    number=43,
                ),
                UpdateTeam(  # update_data_2
                    id=None,
                    competition_code='north-endurance-2023-03-25',
                    participant_code='team-3',
                    name='CKM 3 Updated',
                    number=53,
                ),
                [  # expected_teams_1
                    Team(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1',
                        number=41,
                    ),
                    Team(
                        id=0,
                        participant_code='team-2',
                        name='CKM 2',
                        number=42,
                    ),
                    Team(
                        id=0,
                        participant_code='team-3',
                        name='CKM 3',
                        number=43,
                    ),
                ],
                [  # expected_teams_2
                    Team(
                        id=0,
                        participant_code='team-1',
                        name='CKM 1',
                        number=41,
                    ),
                    Team(
                        id=0,
                        participant_code='team-2',
                        name='CKM 2',
                        number=42,
                    ),
                    Team(
                        id=0,
                        participant_code='team-3',
                        name='CKM 3 Updated',
                        number=53,
                    ),
                ],
            ),
        ],
    )
    def test_handle(
            self,
            competition_code: str,
            update_data_1: UpdateTeam,
            update_data_2: UpdateTeam,
            expected_teams_1: List[Team],
            expected_teams_2: List[Team]) -> None:
        """Test handle method."""
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=competition_code)
        competitions = {competition_code: info}

        # First call to handle method
        handler = UpdateTeamHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        handler.handle(update_data_1)
        assert ([d.dict(exclude={'id': True}) for d in info.teams]
                == [d.dict(exclude={'id': True}) for d in expected_teams_1])

        # Second call to handle method
        handler = UpdateTeamHandler(
            api_url=REAL_API_LTS,
            auth_data=auth_data,
            competitions=competitions)
        model = self._find_team(info, update_data_2.participant_code)
        update_data_2.id = model.id
        handler.handle(update_data_2)
        assert ([d.dict(exclude={'id': True}) for d in info.teams]
                == [d.dict(exclude={'id': True}) for d in expected_teams_2])

    def _find_team(
            self,
            info: CompetitionInfo,
            participant_code: str) -> Team:
        """Find a team in the competition info."""
        for t in info.teams:
            if t.participant_code == participant_code:
                return t
        raise Exception(f'Team "{participant_code}" not found')
