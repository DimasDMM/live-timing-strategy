import requests
from typing import Dict, Optional

from ltspipe.data.competitions import (
    CompetitionStage,
    DiffLap,
    ParticipantTiming,
)
from ltspipe.data.enum import (
    KartStatus,
)


def get_all_timing(
        api_url: str,
        bearer: str,
        competition_id: int) -> Dict[str, ParticipantTiming]:
    """Get timing information of all teams."""
    uri = f'{api_url}/v1/c/{competition_id}/timing'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, list):
        raise Exception(f'Unknown API response ({uri}): {response}')

    timing: Dict[str, ParticipantTiming] = {}
    for item in response:
        if 'participant_code' not in item:
            raise Exception(f'Unknown API response: {response}')
        code = item['participant_code']
        timing[code] = ParticipantTiming.from_dict(item)  # type: ignore

    return timing


def get_timing_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> ParticipantTiming:
    """Get timing information of a specific teams."""
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_by_team(
        api_url: str,
        bearer: str,
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
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')
