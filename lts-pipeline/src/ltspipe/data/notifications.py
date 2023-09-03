from pydantic import Field
from typing import Any, Optional

from ltspipe.base import BaseModel, DictModel, EnumBase


class NotificationType(str, EnumBase):
    """Types of notifications."""

    INIT_ONGOING = 'init-ongoing'
    INIT_FINISHED = 'init-finished'
    ADDED_PIT_IN = 'added-pit-in'
    ADDED_PIT_OUT = 'added-pit-out'
    UPDATED_COMPETITION_METADATA_STATUS = 'updated-competition-metadata-status'
    UPDATED_DRIVER = 'updated-driver'
    UPDATED_TEAM = 'updated-team'
    UPDATED_TIMING_POSITION = 'updated-timing-position'


class Notification(DictModel):
    """Notification data."""

    type: NotificationType
    data: Optional[Any] = Field(default=None)

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            type=raw.get('type'),
            data=raw.get('data', None),
        )
