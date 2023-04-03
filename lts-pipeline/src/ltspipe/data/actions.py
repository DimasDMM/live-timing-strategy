from dataclasses import dataclass
from typing import Any

from ltspipe.enum import EnumBase


class ActionType(EnumBase):
    """Types of actions."""

    INITIALIZE = 'initialize'
    UPDATE = 'update'


@dataclass(frozen=True)
class Action:
    """Apply an action to the data."""

    type: ActionType
    data: Any
