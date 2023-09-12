import requests
from typing import Dict, Optional

from ltspipe.data.competitions import (
    CompetitionStage,
    DiffLap,
    ParticipantTiming,
)
from ltspipe.data.enum import KartStatus


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
        team_id: int) -> Optional[ParticipantTiming]:
    """Get timing information of a specific teams."""
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        # Empty response
        return None

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
        last_time: int,
        number_pits: int,
        pit_time: Optional[int],
        position: int,
        stage: CompetitionStage) -> ParticipantTiming:
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
        'last_time': last_time,
        'number_pits': number_pits,
        'pit_time': pit_time,
        'position': position,
        'stage': stage.value,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_lap_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        lap: int) -> ParticipantTiming:
    """Update timing lap of a team."""
    data = {
        'lap': lap,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/lap'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_last_time_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        last_time: int,
        auto_best_time: bool) -> ParticipantTiming:
    """Update timing last time of a team."""
    data = {
        'last_time': last_time,
        'auto_best_time': auto_best_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/last_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_number_pits_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        number_pits: int) -> ParticipantTiming:
    """Update timing number of pits of a team."""
    data = {
        'number_pits': number_pits,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/number_pits'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_pit_time_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        pit_time: int) -> ParticipantTiming:
    """Update timing pit time of a team."""
    data = {
        'pit_time': pit_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/pit_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore


def update_timing_position_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        position: int,
        auto_other_positions: bool) -> ParticipantTiming:
    """Update timing position of a team."""
    data = {
        'position': position,
        'auto_other_positions': auto_other_positions,
    }
    uri = f'{api_url}/v1/c/{competition_id}/timing/teams/{team_id}/position'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    return ParticipantTiming.from_dict(response)  # type: ignore
