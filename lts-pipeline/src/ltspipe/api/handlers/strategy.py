from typing import Optional

from ltspipe.api.handlers.base import ApiHandler
from ltspipe.api.strategy import add_strategy_pit_stats
from ltspipe.data.base import BaseModel
from ltspipe.data.strategy import (
    AddStrategyPitsStats,
    StrategyPitsStats,
)
from ltspipe.data.auth import AuthData
from ltspipe.data.notifications import Notification, NotificationType
from ltspipe.data.competitions import CompetitionInfo
from ltspipe.exceptions import LtsError


class StrategyPitsStatsHandler(ApiHandler):
    """Handle StrategyPitsStats instances."""

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
        """Add the data of a pit-in."""
        if not isinstance(model, AddStrategyPitsStats):
            raise LtsError(
                'The model must be an instance of AddStrategyPitsStats.')

        strategy = add_strategy_pit_stats(
            api_url=self._api_url,
            bearer=self._auth_data.bearer,
            competition_id=self._info.id,
            pit_in_id=model.pit_in_id,
            best_time=model.best_time,
            avg_time=model.avg_time,
        )

        return self._create_notification(strategy)

    def _create_notification(self, strategy: StrategyPitsStats) -> Notification:
        """Create notification of handler."""
        return Notification(
            type=NotificationType.ADDED_STRATEGY_PITS_STATS,
            data=strategy,
        )
