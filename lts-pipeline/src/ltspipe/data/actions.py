from typing import Any

from ltspipe.data.enum import ActionType
from ltspipe.base import BaseModel


class Action(BaseModel):
    """Apply an action to the data."""

    type: ActionType
    data: Any
