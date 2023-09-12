from typing import Dict, Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.pits import (
    get_last_pit_in_by_team,
    update_pit_in_time_by_team,
)
from ltspipe.api.timing import (
    update_timing_lap_by_team,
    update_timing_last_time_by_team,
    update_timing_number_pits_by_team,
    update_timing_pit_time_by_team,
    update_timing_position_by_team,
)
from ltspipe.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    ParticipantTiming,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)


class UpdateTimingLapHandler(ApiHandler):
    """Handle UpdateTimingLap instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingLap):
            raise Exception(
                'The model must be an instance of UpdateTimingLap.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        participant_timing = update_timing_lap_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            lap=model.lap,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_LAP,
            data=data,
        )


class UpdateTimingLastTimeHandler(ApiHandler):
    """Handle UpdateTimingLastTime instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingLastTime):
            raise Exception(
                'The model must be an instance of UpdateTimingLastTime.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        participant_timing = update_timing_last_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            last_time=model.last_time,
            auto_best_time=model.auto_best_time,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_LAST_TIME,
            data=data,
        )


class UpdateTimingNumberPitsHandler(ApiHandler):
    """Handle UpdateTimingNumberPits instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingNumberPits):
            raise Exception(
                'The model must be an instance of UpdateTimingNumberPits.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        participant_timing = update_timing_number_pits_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            number_pits=model.number_pits,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_NUMBER_PITS,
            data=data,
        )


class UpdateTimingPitTimeHandler(ApiHandler):
    """Handle UpdateTimingPitTime instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingPitTime):
            raise Exception(
                'The model must be an instance of UpdateTimingPitTime.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        # Update time in the last pit-in
        last_pit_in = get_last_pit_in_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
        )
        if last_pit_in is not None:
            _ = update_pit_in_time_by_team(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=info.id,  # type: ignore
                pit_in_id=last_pit_in.id,
                pit_time=model.pit_time,
            )

        # Update time in the timing
        participant_timing = update_timing_pit_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            pit_time=model.pit_time,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_PIT_TIME,
            data=data,
        )


class UpdateTimingPositionHandler(ApiHandler):
    """Handle UpdateTimingPosition instances."""

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._competitions = competitions

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingPosition):
            raise Exception(
                'The model must be an instance of UpdateTimingPosition.')

        competition_code = model.competition_code
        info = self._competitions[competition_code]

        participant_timing = update_timing_position_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=info.id,  # type: ignore
            team_id=model.team_id,
            position=model.position,
            auto_other_positions=model.auto_other_positions,
        )

        return self._create_notification(participant_timing)

    def _create_notification(self, data: ParticipantTiming) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_POSITION,
            data=data,
        )
