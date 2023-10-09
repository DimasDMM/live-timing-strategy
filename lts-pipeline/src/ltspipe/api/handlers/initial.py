from typing import Dict, Optional

from ltspipe.api.competitions_base import (
    add_parsers_settings,
    delete_parsers_settings,
    update_competition_metadata,
)
from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.handlers import (
    _find_driver_by_name,
    _find_team_by_code,
)
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
    InitialData,
    Participant,
)
from ltspipe.data.enum import KartStatus, ParserSettings
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.exceptions import LtsError


class InitialDataHandler(ApiHandler):
    """Handle InitialData instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Initialize the data of a competition."""
        if not isinstance(model, InitialData):
            raise LtsError('The model must be an instance of InitialData.')

        update_competition_metadata(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            status=model.status,
            stage=model.stage,
            remaining_length=model.remaining_length,
        )
        self._add_parsers_settings(settings=model.parsers_settings)
        self._add_teams(participants=model.participants)
        self._add_drivers(participants=model.participants)
        self._update_timing(participants=model.participants, stage=model.stage)

        return self._create_notification()

    def _create_notification(self) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.INITIALIZED_COMPETITION,
        )

    def _add_parsers_settings(
            self,
            settings: Dict[ParserSettings, str]) -> None:
        """Add parser settings to competition."""
        delete_parsers_settings(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,  # type: ignore
        )
        self._info.parser_settings = {}

        for setting_name, setting_value in settings.items():
            add_parsers_settings(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                setting_name=setting_name,
                setting_value=setting_value,
            )
            self._info.parser_settings[setting_name] = setting_value

    def _add_drivers(
            self,
            participants: Dict[str, Participant]) -> None:
        """Add new drivers."""
        for p_code, participant in participants.items():
            if participant.driver_name is None:
                continue

            driver = _find_driver_by_name(
                info=self._info,
                participant_code=p_code,
                driver_name=participant.driver_name,
            )
            if driver is not None:
                _ = update_driver(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=self._info.id,
                    driver_id=driver.id,
                    participant_code=participant.participant_code,
                    name=participant.driver_name,
                    number=participant.kart_number,
                )
                driver.participant_code = participant.participant_code
                driver.name = participant.driver_name
            else:
                team = _find_team_by_code(
                    info=self._info,
                    participant_code=p_code,
                )
                driver = add_driver(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=self._info.id,
                    participant_code=participant.participant_code,
                    name=participant.driver_name,
                    number=participant.kart_number,
                    team_id=(None if team is None else team.id),
                )
                self._info.drivers.append(driver)

    def _add_teams(
            self,
            participants: Dict[str, Participant]) -> None:
        """Add new teams."""
        for p_code, participant in participants.items():
            team = _find_team_by_code(
                info=self._info,
                participant_code=p_code,
            )
            if team is not None:
                _ = update_team(
                    api_url=self._api_url,
                    bearer=self._auth_data.bearer,
                    competition_id=self._info.id,
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
                    competition_id=self._info.id,
                    participant_code=participant.participant_code,
                    name=participant.team_name,
                    number=participant.kart_number,
                )
                self._info.teams.append(team)

    def _update_timing(
            self,
            participants: Dict[str, Participant],
            stage: CompetitionStage) -> None:
        """Update timing data of the competition."""
        for p_code, participant in participants.items():
            team = _find_team_by_code(
                info=self._info,
                participant_code=p_code,
            )
            if team is None:
                raise LtsError(
                    f'Team with code={p_code} could not be found.')

            if participant.driver_name is not None:
                driver = _find_driver_by_name(
                    info=self._info,
                    participant_code=p_code,
                    driver_name=participant.driver_name,
                )
                if driver is None:
                    driver_name = participant.driver_name
                    raise LtsError(
                        f'Driver with name={driver_name} could not be found.')
                driver_id = driver.id
            else:
                driver_id = None

            update_timing_by_team(
                self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                team_id=team.id,
                driver_id=driver_id,
                best_time=participant.best_time,
                gap=participant.gap,
                fixed_kart_status=None,
                interval=participant.interval,
                kart_status=KartStatus.UNKNOWN,
                lap=participant.laps,
                number_pits=participant.number_pits,
                pit_time=participant.pit_time,
                position=participant.position,
                stage=stage,
                last_time=participant.last_time,
                auto_best_time=False,
                auto_other_positions=False,
            )
