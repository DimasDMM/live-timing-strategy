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
        best_time: int,
        fixed_kart_status: Optional[KartStatus],
        interval: DiffLap,
        kart_status: KartStatus,
        lap: int,
        number_pits: int,
        pit_time: Optional[int],
        position: int,
        stage: CompetitionStage,
        time: int) -> None:
    """Update timing data of a team."""
    data = {
        'best_time': best_time,
        'driver_id': driver_id,
        'fixed_kart_status': (None if fixed_kart_status is None
                              else fixed_kart_status.value),
        'kart_status': kart_status.value,
        'interval': interval.value,
        'interval_unit': interval.unit.value,
        'lap': lap,
        'number_pits': number_pits,
        'pit_time': pit_time,
        'position': position,
        'stage': stage.value,
        'time': time,
    }
    uri = f'{api_url}/v1/competitions/{competition_id}/timing/team/{team_id}'
    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')
