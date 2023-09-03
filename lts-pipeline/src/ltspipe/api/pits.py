import requests
from typing import Optional

from ltspipe.data.competitions import (
    KartStatus,
    PitIn,
    PitOut,
)


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
        'fixed_kart_status': None,
    }

    uri = f'{api_url}/v1/c/{competition_id}/pits/in'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return _build_pit_in(response)


def add_pit_out(
        api_url: str,
        bearer: str,
        competition_id: int,
        kart_status: KartStatus,
        driver_id: Optional[int] = None,
        team_id: Optional[int] = None) -> PitOut:
    """
    Add a pit-out.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        kart_status (KartStatus): Status of the kart.
        driver_id (int | None): ID of the driver if there is any.
        team_id (int | None): ID of the team if there is any.

    Returns:
        PitOut: New pit-out instance.
    """
    data = {
        'team_id': team_id,
        'driver_id': driver_id,
        'kart_status': kart_status.value,
        'fixed_kart_status': None,
    }

    uri = f'{api_url}/v1/c/{competition_id}/pits/out'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return _build_pit_out(response)
