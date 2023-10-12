import requests
from typing import Dict, List, Optional

from ltspipe.data.competitions import (
    CompetitionStage,
    DiffLap,
    Timing,
)
from ltspipe.data.enum import KartStatus
from ltspipe.exceptions import LtsError


def get_all_timing(
        api_url: str,
        bearer: str,
        competition_id: int) -> Dict[str, Timing]:
    """Get timing information of all teams."""
    uri = f'{api_url}/v1/c/{competition_id}/timing'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, list):
        raise LtsError(f'Unknown API response ({uri}): {response}')

    timing: Dict[str, Timing] = {}
    for item in response:
        if 'participant_code' not in item:
            raise LtsError(f'Unknown API response: {response}')
        code = item['participant_code']
        timing[code] = Timing.from_dict(item)  # type: ignore

    return timing


def get_timing_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> Optional[Timing]:
    """Get timing information of a specific team."""
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        # Empty response
        return None

    return Timing.from_dict(response)  # type: ignore


def get_timing_history_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> List[Timing]:
    """Get history timing information of a specific team."""
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/history'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore
    timing: List[Timing] = []
    for item in response:
        model: Timing = Timing.from_dict(  # type: ignore
                                                               item)
        timing.append(model)

    return timing


def update_timing_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        driver_id: Optional[int],
        best_time: int,
        gap: Optional[DiffLap],
        fixed_kart_status: Optional[KartStatus],
        interval: Optional[DiffLap],
        kart_status: KartStatus,
        lap: int,
        last_time: int,
        number_pits: int,
        pit_time: Optional[int],
        position: int,
        stage: CompetitionStage,
        auto_best_time: bool = True,
        auto_other_positions: bool = True) -> Timing:
    """Update timing data of a team."""
    data = {
        'best_time': best_time,
        'driver_id': driver_id,
        'fixed_kart_status': (None if fixed_kart_status is None
                              else fixed_kart_status.value),
        'gap': None if gap is None else gap.value,
        'gap_unit': None if gap is None else gap.unit.value,
        'kart_status': kart_status.value,
        'interval': None if interval is None else interval.value,
        'interval_unit': None if interval is None else interval.unit.value,
        'lap': lap,
        'last_time': last_time,
        'number_pits': number_pits,
        'pit_time': pit_time,
        'position': position,
        'stage': stage.value,
        'auto_best_time': auto_best_time,
        'auto_other_positions': auto_other_positions,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_driver_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        driver_id: Optional[int]) -> Timing:
    """Update timing driver of a team."""
    data = {
        'driver_id': driver_id,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/driver'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_best_time_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        best_time: int) -> Timing:
    """Update timing best time of a team."""
    data = {
        'best_time': best_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/best_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_lap_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        lap: int) -> Timing:
    """Update timing lap of a team."""
    data = {
        'lap': lap,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/lap'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_last_time_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        last_time: int,
        auto_best_time: bool) -> Timing:
    """Update timing last time of a team."""
    data = {
        'last_time': last_time,
        'auto_best_time': auto_best_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/last_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_number_pits_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        number_pits: int) -> Timing:
    """Update timing number of pits of a team."""
    data = {
        'number_pits': number_pits,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/number_pits'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_pit_time_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        pit_time: Optional[int]) -> Timing:
    """Update timing pit time of a team."""
    data = {
        'pit_time': pit_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/pit_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore


def update_timing_position_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        position: int,
        auto_other_positions: bool) -> Timing:
    """Update timing position of a team."""
    data = {
        'position': position,
        'auto_other_positions': auto_other_positions,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/position'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return Timing.from_dict(response)  # type: ignore
