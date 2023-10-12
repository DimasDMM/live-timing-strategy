from typing import Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.pits import (
    get_last_pit_in_by_team,
    update_pit_in_time_by_id,
)
from ltspipe.api.timing import (
    get_all_timing,
    update_timing_best_time_by_team,
    update_timing_lap_by_team,
    update_timing_last_time_by_team,
    update_timing_number_pits_by_team,
    update_timing_pit_time_by_team,
    update_timing_position_by_team,
)
from ltspipe.data.base import BaseModel
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import (
    CompetitionInfo,
    Timing,
    UpdateTimingBestTime,
    UpdateTimingLap,
    UpdateTimingLastTime,
    UpdateTimingNumberPits,
    UpdateTimingPitTime,
    UpdateTimingPosition,
)
from ltspipe.exceptions import LtsError


class UpdateTimingBestTimeHandler(ApiHandler):
    """Handle UpdateTimingBestTime instances."""

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
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingBestTime):
            raise LtsError(
                'The model must be an instance of UpdateTimingBestTime.')

        timing = update_timing_best_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            best_time=model.best_time,
        )
        self._info.timing[timing.participant_code] = timing

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_BEST_TIME,
            data=data,
        )


class UpdateTimingLapHandler(ApiHandler):
    """Handle UpdateTimingLap instances."""

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
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingLap):
            raise LtsError(
                'The model must be an instance of UpdateTimingLap.')

        timing = update_timing_lap_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            lap=model.lap,
        )
        self._info.timing[timing.participant_code] = timing

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
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
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingLastTime):
            raise LtsError(
                'The model must be an instance of UpdateTimingLastTime.')

        timing = update_timing_last_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            last_time=model.last_time,
            auto_best_time=model.auto_best_time,
        )
        self._info.timing[timing.participant_code] = timing

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
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
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingNumberPits):
            raise LtsError(
                'The model must be an instance of UpdateTimingNumberPits.')

        timing = update_timing_number_pits_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            number_pits=model.number_pits,
        )
        self._info.timing[timing.participant_code] = timing

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
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
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingPitTime):
            raise LtsError(
                'The model must be an instance of UpdateTimingPitTime.')

        # Update time in the last pit-in
        last_pit_in = get_last_pit_in_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
        )
        if last_pit_in is not None:
            _ = update_pit_in_time_by_id(
                api_url=self._api_url,
                bearer=self._auth_data.bearer,
                competition_id=self._info.id,
                pit_in_id=last_pit_in.id,
                pit_time=model.pit_time,
            )

        # Update time in the timing
        timing = update_timing_pit_time_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            pit_time=model.pit_time,
        )
        self._info.timing[timing.participant_code] = timing

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
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
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def handle(self, model: BaseModel) -> Optional[Notification]:
        """Update the timing position of a participant."""
        if not isinstance(model, UpdateTimingPosition):
            raise LtsError(
                'The model must be an instance of UpdateTimingPosition.')

        timing = update_timing_position_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=model.team_id,
            position=model.position,
            auto_other_positions=model.auto_other_positions,
        )

        # Update all timings since there might be changes
        self._info.timing = get_all_timing(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
        )

        return self._create_notification(timing)

    def _create_notification(self, data: Timing) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.UPDATED_TIMING_POSITION,
            data=data,
        )
