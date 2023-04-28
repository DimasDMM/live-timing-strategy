from abc import ABC, abstractmethod
from typing import Optional

from ltspipe.base import BaseModel
from ltspipe.data.notifications import Notification


class ApiHandler(ABC):
    """Handler of API data."""

    @abstractmethod
    def handle(self, model: BaseModel) -> Optional[Notification]:
        """
        Handle a model.

        If it does anything with the model, it might return a notification
        instance with the information of the process applied to the model.

        Params:
            model (BaseModel): Model data.

        Returns
            Notification | None: Notification instance.
        """
        raise NotImplementedError
