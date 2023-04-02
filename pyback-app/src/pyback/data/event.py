from dataclasses import asdict, dataclass, field
from typing import Dict, Optional

from pyback.data.time import DiffLap


@dataclass
class Participant:
    """Details of a participant."""

    code: str
    ranking: Optional[int] = field(default=None)
    kart_number: Optional[int] = field(default=None)
    team_name: Optional[str] = field(default=None)
    driver_name: Optional[str] = field(default=None)
    last_lap_time: Optional[int] = field(default=None)
    best_time: Optional[int] = field(default=None)
    gap: Optional[DiffLap] = field(default=None)
    interval: Optional[DiffLap] = field(default=None)
    laps: Optional[int] = field(default=None)
    pits: Optional[int] = field(default=None)
    pit_time: Optional[int] = field(default=None)

    def to_dict(self) -> dict:
        """Transform into a dictionary."""
        return dict(asdict(self).items())


@dataclass
class InitialData:
    """Details about the initial data of an event."""

    headers: Dict[str, str]
    participants: Dict[str, Participant]

    def to_dict(self) -> dict:
        """Transform into a dictionary."""
        return dict(asdict(self).items())
