import statistics as st
from typing import Any, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.auth import AuthData
from ltspipe.data.competitions import (
    CompetitionInfo,
    PitIn,
    Timing,
)
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.strategy import AddStrategyPitsStats
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.api.pits import get_pits_in_by_team
from ltspipe.api.timing import get_timing_history_by_team


class StrategyPitsStatsParser(Parser):
    """
    Compute the strategy pits stats.
    """

    def __init__(
            self,
            api_url: str,
            auth_data: AuthData,
            info: CompetitionInfo) -> None:
        """Construct."""
        self._api_url = api_url
        self._auth_data = auth_data
        self._info = info

    def parse(
            self,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        if not isinstance(data, Notification):
            return [], False

        if data.type != NotificationType.ADDED_PIT_IN:
            # Ignore notification
            return [], False
        elif not isinstance(data.data, PitIn):
            raise LtsError('Unknown data content of pit-in notification')

        action = self._compute_strategy(data=data.data)

        if action is None:
            return [], False
        else:
            return [action], True

    def _compute_strategy(
            self,
            data: PitIn) -> Optional[Action]:
        """Compute the strategy."""
        timing_history = self._get_and_filter_history_timing(data)
        if len(timing_history) == 0:
            return None

        best_time, avg_time = self._compute_times(timing_history)

        return Action(
            type=ActionType.ADD_STRATEGY_PITS_STATS,
            data=AddStrategyPitsStats(
                pit_in_id=data.id,
                best_time=best_time,
                avg_time=avg_time,
            ),
        )

    def _compute_times(
            self,
            timing_history: List[Timing],
            top_avg_times: int = 5) -> Tuple[int, int]:
        """
        Compute the best and the average timing.

        Note that the average time is not computed with all times but only with
        the top N times.
        """
        timing_history = sorted(
            timing_history, key=lambda x: x.last_time, reverse=False)

        best_time = timing_history[0].last_time

        top_times = [x.last_time for x in timing_history[:top_avg_times]]
        avg_time = int(st.mean(top_times))

        return best_time, avg_time

    def _get_and_filter_history_timing(
            self,
            data: PitIn) -> List[Timing]:
        """Get the timing records between the last pit-in and before that."""
        if data.team_id is None:
            return []

        pits_in = get_pits_in_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=data.team_id,
        )
        timing_history = get_timing_history_by_team(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            team_id=data.team_id,
        )
        timing_history = [
            x for x in timing_history
            if x.last_time > 0 and x.lap is not None and x.lap > 0]

        if len(pits_in) <= 1:
            # No need to filter since there is only one pit-in
            return timing_history

        # Pick the pit-in before the last added pit-in
        previous_pit_in = None
        for x in pits_in:
            if ((previous_pit_in is None
                    or x.lap > previous_pit_in.lap)
                    and x.id != data.id):
                previous_pit_in = x

        if previous_pit_in is None or previous_pit_in.lap == 0:
            # Cannot determine when was the previous pit-in
            return []

        # Filter timing
        from_lap = previous_pit_in.lap
        timing_history = [x for x in timing_history
                          if x.lap > from_lap]  # type: ignore

        if data.lap is not None and data.lap > 0:
            to_lap = data.lap
            timing_history = [x for x in timing_history
                              if x.lap < to_lap]  # type: ignore

        return timing_history
