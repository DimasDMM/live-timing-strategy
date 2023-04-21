import requests
from typing import Optional

from ltspipe.data.competitions import (
    CompetitionStage,
    DiffLap,
)
from ltspipe.data.enum import (
    KartStatus,
)


def update_timing_by_team(
        api_url: str,
        competition_id: int,
        team_id: int,
        driver_id: Optional[int],
        position: Optional[int],
        time: Optional[int],
        best_time: Optional[int],
        lap: Optional[int],
        interval: Optional[DiffLap],
        stage: Optional[CompetitionStage],
        pits: Optional[int],
        kart_status: Optional[KartStatus],
        fixed_kart_status: Optional[KartStatus],
        number_pits: Optional[int]) -> None:
    """Update timing data of a team."""
    interval_value = None if interval is None else interval.value
    interval_unit = None if interval is None else interval.unit.value
    data = {
        'driver_id': driver_id,
        'position': position,
        'time': time,
        'best_time': best_time,
        'lap': lap,
        'interval': interval_value,
        'interval_unit': interval_unit,
        'stage': None if stage is None else stage.value,
        'pits': pits,
        'kart_status': None if kart_status is None else kart_status.value,
        'fixed_kart_status': (None if fixed_kart_status is None
                              else fixed_kart_status.value),
        'number_pits': number_pits,
    }
    uri = f'{api_url}/v1/competitions/{competition_id}/timing/team/{team_id}'
    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')
