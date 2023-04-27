from typing import Dict, List, Optional

from ltspipe.api.competitions_base import (
    add_parsers_settings,
    delete_parsers_settings,
    update_competition_metadata,
)
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.participants import (
    add_driver,
    add_team,
    update_driver,
    update_team,
)
from ltspipe.api.timing import update_timing_by_team
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    Driver,
    InitialData,
    Participant,
    Team,
)
from ltspipe.data.enum import KartStatus, ParserSettings


class InitialDataHandler(ApiHandler):
    """Handle InitialData instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> None:
        """Initialize the data of a competition."""
        if not isinstance(model, InitialData):
            raise Exception('The model must be an instance of InitialData.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]
        if info.id is None:
            raise Exception(
                f'ID of the competition cannot be None: {competition_code}')

        update_competition_metadata(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,
            status=model.status,
            stage=model.stage,
            remaining_length=model.remaining_length,
        )
        self._add_parsers_settings(info=info, settings=model.parsers_settings)
        self._add_teams(info=info, participants=model.participants)
        self._add_drivers(info=info, participants=model.participants)
        self._update_timing(info=info, participants=model.participants)

    def _add_parsers_settings(
            self,
            info: CompetitionInfo,
            settings: Dict[ParserSettings, str]) -> None:
        """Add parser settings to competition."""
        delete_parsers_settings(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
        )
        info.parser_settings = {}

        for setting_name, setting_value in settings.items():
            add_parsers_settings(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                setting_name=setting_name,
                setting_value=setting_value,
            )
            info.parser_settings[setting_name] = setting_value

    def _add_drivers(
            self,
            info: CompetitionInfo,
            participants: Dict[str, Participant]) -> None:
        """Add new drivers."""
        for p_code, participant in participants.items():
            if participant.driver_name is None:
                continue

            driver = self._find_driver_by_name(
                name=participant.driver_name,
                drivers=info.drivers,
            )
            if driver is not None:
                _ = update_driver(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=info.id,  # type: ignore
                    driver_id=driver.id,
                    participant_code=participant.participant_code,
                    name=participant.driver_name,
                    number=participant.kart_number,
                )
                driver.participant_code = participant.participant_code
                driver.name = participant.driver_name
            else:
                team = self._find_team_by_code(
                    code=p_code,
                    teams=info.teams,
                )
                driver = add_driver(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=info.id,  # type: ignore
                    participant_code=participant.participant_code,
                    name=participant.driver_name,
                    number=participant.kart_number,
                    team_id=(None if team is None else team.id),
                )
                info.drivers.append(driver)

    def _add_teams(
            self,
            info: CompetitionInfo,
            participants: Dict[str, Participant]) -> None:
        """Add new teams."""
        for p_code, participant in participants.items():
            team = self._find_team_by_code(p_code, info.teams)
            if team is not None:
                _ = update_team(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=info.id,  # type: ignore
                    team_id=team.id,
                    participant_code=participant.participant_code,
                    name=participant.team_name,  # type: ignore
                    number=participant.kart_number,
                )
                team.participant_code = participant.participant_code
                team.name = participant.team_name  # type: ignore
            else:
                if (participant.team_name is None
                        or participant.kart_number is None):
                    continue

                team = add_team(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=info.id,  # type: ignore
                    participant_code=participant.participant_code,
                    name=participant.team_name,
                    number=participant.kart_number,
                )
                info.teams.append(team)

    def _update_timing(
            self,
            info: CompetitionInfo,
            participants: Dict[str, Participant]) -> None:
        """Update timing data of the competition."""
        for p_code, participant in participants.items():
            team = self._find_team_by_code(p_code, info.teams)
            if team is None:
                raise Exception(
                    f'Team with code={p_code} could not be found.')

            driver_name = participant.driver_name
            if driver_name is not None:
                driver = self._find_driver_by_name(
                    name=driver_name,
                    drivers=info.drivers,
                )
                if driver is None:
                    raise Exception(
                        f'Driver with name={driver_name} could not be found.')
                driver_id = driver.id
            else:
                driver_id = None

            update_timing_by_team(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                team_id=team.id,
                driver_id=driver_id,
                best_time=participant.best_time,
                fixed_kart_status=None,
                interval=participant.interval,
                kart_status=KartStatus.UNKNOWN,
                lap=participant.laps,
                number_pits=participant.number_pits,
                pit_time=participant.pit_time,
                position=participant.ranking,
                stage=CompetitionStage.FREE_PRACTICE,  # TODO
                time=participant.last_lap_time,
            )

    def _find_team_by_code(
            self,
            code: str,
            teams: List[Team]) -> Optional[Team]:
        """Find a team instance by the code."""
        for team in teams:
            if team.participant_code == code:
                return team
        return None

    def _find_driver_by_name(
            self,
            name: str,
            drivers: List[Driver]) -> Optional[Driver]:
        """Find a driver instance by the name."""
        for driver in drivers:
            if driver.name == name:
                return driver
        return None
