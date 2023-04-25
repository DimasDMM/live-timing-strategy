from abc import ABC, abstractmethod

from ltspipe.base import BaseModel


class ApiHandler(ABC):
    """Handler of API data."""

    @abstractmethod
    def handle(self, model: BaseModel) -> None:
        """Handle a model."""
        raise NotImplementedError
