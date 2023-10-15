import requests
from typing import List, Optional

from ltspipe.data.competitions import (
    KartStatus,
    PitIn,
    PitOut,
)
from ltspipe.exceptions import LtsError


def _build_pit_in(raw: dict) -> PitIn:
    """Build a pit-in instance from a dictionary."""
    ignore_keys = {'competition_id', 'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    pit_in: PitIn = PitIn.from_dict(raw)  # type: ignore
    return pit_in


def _build_pit_out(raw: dict) -> PitOut:
    """Build a pit-out instance from a dictionary."""
    ignore_keys = {'competition_id', 'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    pit_out: PitOut = PitOut.from_dict(raw)  # type: ignore
    return pit_out


def add_pit_in(
        api_url: str,
        bearer: str,
        competition_id: int,
        kart_status: KartStatus,
        fixed_kart_status: Optional[KartStatus],
        pit_time: int,
        lap: int,
        driver_id: Optional[int] = None,
        team_id: Optional[int] = None) -> PitIn:
    """
    Add a pit-in.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        kart_status (KartStatus): Status of the kart.
        fixed_kart_status (KartStatus | None): Fixed status of the kart.
        pit_time (int): Time in pit.
        lap (int): Lap when the pit-in occurs.
        driver_id (int | None): ID of the driver if there is any.
        team_id (int | None): ID of the team if there is any.

    Returns:
        PitIn: New pit-in instance.
    """
    data = {
        'team_id': team_id,
        'driver_id': driver_id,
        'lap': lap,
        'pit_time': pit_time,
        'kart_status': kart_status.value,
        'fixed_kart_status': (None if fixed_kart_status is None
                              else fixed_kart_status.value),
    }

    uri = f'{api_url}/v1/c/{competition_id}/pits/in'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_pit_in(response)


def add_pit_out(
        api_url: str,
        bearer: str,
        competition_id: int,
        kart_status: KartStatus,
        fixed_kart_status: Optional[KartStatus],
        driver_id: Optional[int] = None,
        team_id: Optional[int] = None) -> PitOut:
    """
    Add a pit-out.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        kart_status (KartStatus): Status of the kart.
        fixed_kart_status (KartStatus | None): Fixed status of the kart.
        driver_id (int | None): ID of the driver if there is any.
        team_id (int | None): ID of the team if there is any.

    Returns:
        PitOut: New pit-out instance.
    """
    data = {
        'team_id': team_id,
        'driver_id': driver_id,
        'kart_status': kart_status.value,
        'fixed_kart_status': fixed_kart_status,
    }

    uri = f'{api_url}/v1/c/{competition_id}/pits/out'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_pit_out(response)


def get_pits_in_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> List[PitIn]:
    """Get all pits-in of a team."""
    uri = f'{api_url}/v1/c/{competition_id}/pits/in/filter/team/{team_id}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore
    pits_in: List[PitIn] = []
    for item in response:
        model = _build_pit_in(item)  # type: ignore
        pits_in.append(model)

    return pits_in


def get_last_pit_in_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> Optional[PitIn]:
    """Get last pit-in of a team."""
    uri = f'{api_url}/v1/c/{competition_id}/pits/in/filter/team/{team_id}/last'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    return _build_pit_in(response)


def get_last_pit_out_by_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> Optional[PitOut]:
    """Get last pit-out of a team."""
    uri = f'{api_url}/v1/c/{competition_id}/pits/out/filter/team/{team_id}/last'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    return _build_pit_out(response)


def update_pit_in_time_by_id(
        api_url: str,
        bearer: str,
        competition_id: int,
        pit_in_id: int,
        pit_time: int) -> PitIn:
    """Update pit-in time of a team."""
    data = {
        'pit_time': pit_time,
    }
    uri = f'{api_url}/v1/c/{competition_id}/pits/in/{pit_in_id}/pit_time'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_pit_in(response)


def update_pit_out_driver_by_id(
        api_url: str,
        bearer: str,
        competition_id: int,
        pit_out_id: int,
        driver_id: int) -> PitOut:
    """Update pit-out driver of a team."""
    data = {
        'driver_id': driver_id,
    }
    uri = f'{api_url}/v1/c/{competition_id}/pits/out/{pit_out_id}/driver'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_pit_out(response)
