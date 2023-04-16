import os
from typing import Optional

from ltspipe.data.competitions import DiffLap

BASE_PATH = 'tests/data/messages'


def build_participant(
        participant_code: str,
        ranking: Optional[int] = None,
        kart_number: Optional[int] = None,
        team_name: Optional[str] = None,
        driver_name: Optional[str] = None,
        last_lap_time: Optional[int] = None,
        best_time: Optional[int] = None,
        gap: Optional[DiffLap] = None,
        interval: Optional[DiffLap] = None,
        laps: Optional[int] = None,
        pits: Optional[int] = None,
        pit_time: Optional[int] = None,
) -> dict:
    """Build participant data as a dictionary."""
    return {
        'participant_code': participant_code,
        'ranking': ranking,
        'kart_number': kart_number,
        'team_name': team_name,
        'driver_name': driver_name,
        'last_lap_time': last_lap_time,
        'best_time': best_time,
        'gap': gap,
        'interval': interval,
        'laps': laps,
        'pits': pits,
        'pit_time': pit_time,
    }


def load_raw_message(filename: str) -> str:
    """Load a raw message."""
    filepath = os.path.join(BASE_PATH, filename)
    with open(filepath, 'r') as fp:
        return fp.read()
