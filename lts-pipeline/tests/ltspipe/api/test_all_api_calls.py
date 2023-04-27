from typing import List

from ltspipe.api.auth import refresh_bearer
from ltspipe.api.competitions_base import build_competition_info
from ltspipe.api.participants import (
    add_driver,
    add_team,
    get_all_drivers,
    get_all_teams,
    get_driver,
    get_team,
    update_driver,
    update_team,
)
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import (
    CompetitionInfo,
    DiffLap,
    Driver,
    Participant,
    Team,
)
from ltspipe.data.enum import (
    LengthUnit,
)
from tests.fixtures import (
    AUTH_KEY,
    REAL_API_LTS,
    TEST_COMPETITION_CODE,
)
from tests.helpers import (
    DatabaseTest,
    create_competition,
)


class TestAllApiCalls(DatabaseTest):
    """
    Functional test with all API calls.

    Important: Since these tests are functional, they require that there are
    a database and an API REST running.
    """

    PARTICIPANTS = [
        Participant(
            best_time=64882,  # 1:04.882
            driver_name='CKM 1 Driver 1',
            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
            kart_number=41,
            laps=5,
            last_lap_time=65142,  # 1:05.142
            number_pits=0,
            participant_code='r5625',
            pit_time=None,
            ranking=1,
            team_name='CKM 1',
        ),
        Participant(
            best_time=64890,  # 1:04.890
            driver_name='CKM 1 Driver 2',
            gap=DiffLap(value=0, unit=LengthUnit.MILLIS),
            interval=DiffLap(value=0, unit=LengthUnit.MILLIS),
            kart_number=41,
            laps=5,
            last_lap_time=65460,  # 1:05.460
            number_pits=1,
            participant_code='r5625',
            pit_time=None,
            ranking=1,
            team_name='CKM 1',
        ),
        Participant(
            best_time=64941,  # 1:04.941
            driver_name='CKM 2 Driver 1',
            gap=DiffLap(
                value=1,  # 1 lap
                unit=LengthUnit.LAPS.value,
            ),
            interval=DiffLap(
                value=12293,  # 12.293
                unit=LengthUnit.MILLIS.value,
            ),
            kart_number=42,
            laps=5,
            last_lap_time=65411,  # 1:05.411
            number_pits=2,
            participant_code='r5626',
            pit_time=54000,  # 54.
            ranking=2,
            team_name='CKM 2',
        ),
    ]

    def test_all_api_calls(self) -> None:
        """Test all API calls."""
        # Do authentication and create a test competition
        auth_data = refresh_bearer(REAL_API_LTS, AUTH_KEY)
        competition_id = create_competition(
            REAL_API_LTS, bearer=auth_data.bearer)

        # Initialize info of the competition
        info = build_competition_info(
            REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_code=TEST_COMPETITION_CODE)
        assert info.id == competition_id

        # Add teams and drivers and validate that data was sent successfully
        self._add_teams(info, REAL_API_LTS, auth_data, self.PARTICIPANTS)
        self._add_drivers(info, REAL_API_LTS, auth_data, self.PARTICIPANTS)

        retrieved_teams = get_all_teams(
            REAL_API_LTS, auth_data.bearer, competition_id)
        retrieved_drivers = get_all_drivers(
            REAL_API_LTS, auth_data.bearer, competition_id)
        self._compare_teams(retrieved_teams, self.PARTICIPANTS)
        self._compare_drivers(info, retrieved_drivers, self.PARTICIPANTS)

        # Update the name of a driver and, also, a team
        driver = retrieved_drivers[0]
        team = retrieved_teams[0]
        self._update_single_driver(
            REAL_API_LTS, auth_data, competition_id, driver)
        self._update_single_team(
            REAL_API_LTS, auth_data, competition_id, team)

    def _update_single_driver(
            self,
            api_lts: str,
            auth_data: AuthData,
            competition_id: int,
            driver: Driver) -> None:
        """Update a driver and validate that the data was modified."""
        new_name = f'{driver.name} - Updated'
        update_driver(
            api_url=REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_id=competition_id,
            driver_id=driver.id,
            participant_code=driver.participant_code,
            name=new_name,
            number=driver.number,
        )
        updated_driver = get_driver(
            api_url=api_lts,
            bearer=auth_data.bearer,
            competition_id=competition_id,
            driver_id=driver.id)
        assert updated_driver is not None
        assert updated_driver.name == new_name

    def _update_single_team(
            self,
            api_lts: str,
            auth_data: AuthData,
            competition_id: int,
            team: Team) -> None:
        """Update a team and validate that the data was modified."""
        new_name = f'{team.name} - Updated'
        update_team(
            api_url=REAL_API_LTS,
            bearer=auth_data.bearer,
            competition_id=competition_id,
            team_id=team.id,
            name=new_name,
            number=team.number,
            participant_code=team.participant_code,
        )
        updated_team = get_team(
            api_url=api_lts,
            bearer=auth_data.bearer,
            competition_id=competition_id,
            team_id=team.id)
        assert updated_team is not None
        assert updated_team.name == new_name

    def _compare_drivers(
            self,
            info: CompetitionInfo,
            given_drivers: List[Driver],
            expected_participants: List[Participant]) -> None:
        """Compare the given drivers with the list of participants."""
        code_to_team_id = {team.participant_code: team.id
                           for team in info.teams}

        given_drivers = sorted(given_drivers, key=lambda t: t.name)
        expected_participants = sorted(
            expected_participants, key=lambda p: p.driver_name)

        participant_codes = set()
        expected_drivers: List[Driver] = []
        for p in expected_participants:
            d = Driver(
                id=0,
                participant_code=p.participant_code,
                name=p.driver_name,
                number=p.kart_number,
                team_id=code_to_team_id[p.participant_code],
                total_driving_time=0,
                partial_driving_time=0,
            )
            expected_drivers.append(d)
            participant_codes.add(p.participant_code)

        assert ([t.dict(exclude={'id': True}) for t in given_drivers]
                == [t.dict(exclude={'id': True}) for t in expected_drivers])

    def _compare_teams(
            self,
            given_teams: List[Team],
            expected_participants: List[Participant]) -> None:
        """Compare the given teams with the list of participants."""
        given_teams = sorted(given_teams, key=lambda t: t.name)
        expected_participants = sorted(
            expected_participants, key=lambda p: p.team_name)

        participant_codes = set()
        expected_teams: List[Team] = []
        for p in expected_participants:
            if p.participant_code in participant_codes:
                continue
            t = Team(
                id=0,
                participant_code=p.participant_code,
                name=p.team_name,
                number=p.kart_number,
            )
            expected_teams.append(t)
            participant_codes.add(p.participant_code)

        assert ([t.dict(exclude={'id': True}) for t in given_teams]
                == [t.dict(exclude={'id': True}) for t in expected_teams])

    def _add_drivers(
            self,
            info: CompetitionInfo,
            api_lts: str,
            auth_data: AuthData,
            participants: List[Participant]) -> None:
        """Add new drivers."""
        code_to_team_id = {team.participant_code: team.id
                           for team in info.teams}

        for participant in participants:
            p_code = participant.participant_code
            team_id = code_to_team_id[p_code]

            driver = add_driver(
                api_url=api_lts,
                bearer=auth_data.bearer,
                competition_id=info.id,
                participant_code=p_code,
                name=participant.driver_name,
                number=participant.kart_number,
                team_id=team_id,
            )
            info.drivers.append(driver)

    def _add_teams(
            self,
            info: CompetitionInfo,
            api_lts: str,
            auth_data: AuthData,
            participants: List[Participant]) -> None:
        """Add new teams."""
        added_codes = set()
        for participant in participants:
            p_code = participant.participant_code
            if p_code in added_codes:
                continue

            team = add_team(
                api_url=api_lts,
                bearer=auth_data.bearer,
                competition_id=info.id,
                participant_code=p_code,
                name=participant.team_name,
                number=participant.kart_number,
            )
            info.teams.append(team)
            added_codes.add(p_code)
