import requests
from typing import Dict, List, Optional

from ltspipe.data.competitions import (
    Driver,
    Team,
)
from ltspipe.exceptions import LtsError


def _build_driver(raw: dict) -> Driver:
    """Build a driver instance from a dictionary."""
    ignore_keys = {'competition_id', 'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    driver: Driver = Driver.from_dict(raw)  # type: ignore
    return driver


def _build_team(raw: dict) -> Team:
    """Build a team instance from a dictionary."""
    ignore_keys = {'competition_id', 'drivers', 'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    team: Team = Team.from_dict(raw)  # type: ignore
    return team


def add_driver(
        api_url: str,
        bearer: str,
        competition_id: int,
        participant_code: str,
        name: str,
        number: int,
        team_id: Optional[int] = None) -> Driver:
    """
    Add a new driver.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        participant_code (str): Code of the driver.
        name (str): Name of the driver.
        number (int): Number of the driver.
        team_id (int | None): ID of the team if there is any.

    Returns:
        Driver: New driver instance.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }

    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/c/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers'

    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_driver(response)


def add_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        participant_code: str,
        name: str,
        number: int) -> Team:
    """
    Add a new team.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        participant_code (str): Code of the team.
        name (str): Name of the team.
        number (int): Number of the team.

    Returns:
        Team: New team instance.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }
    uri = f'{api_url}/v1/c/{competition_id}/teams'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_team(response)


def get_driver_by_id(
        api_url: str,
        bearer: str,
        competition_id: int,
        driver_id: int) -> Optional[Driver]:
    """
    Get a single driver.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        driver_id (int): ID of the driver.

    Returns:
        Optional[Driver]: Instance of the driver.
    """
    uri = f'{api_url}/v1/c/{competition_id}/drivers/{driver_id}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    return _build_driver(response)


def get_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int) -> Optional[Team]:
    """
    Get a single team.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        team_id (int): ID of the team.

    Returns:
        Optional[Team]: Instance of the team.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    uri = f'{api_url}/v1/c/{competition_id}/teams/{team_id}'

    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    return _build_team(response)


def get_team_by_code(
        api_url: str,
        bearer: str,
        competition_id: int,
        participant_code: str) -> Optional[Team]:
    """
    Get a team by its participant code.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        participant_code (str): Code of the participant.

    Returns:
        Optional[Team]: Instance of the team.
    """
    uri = (f'{api_url}/v1/c/{competition_id}/teams/'
           f'filter/code/{participant_code}')
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    return _build_team(response)


def get_all_drivers(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: Optional[int] = None) -> List[Driver]:
    """
    Get all drivers.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        team_id (int | None): ID of the team if there is any.

    Returns:
        List[Driver]: List of drivers.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/c/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers'

    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore
    drivers: List[Driver] = []
    for item in response:
        drivers.append(_build_driver(item))

    return drivers


def get_all_teams(
        api_url: str,
        bearer: str,
        competition_id: int) -> Dict[str, Team]:
    """
    Get all teams.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.

    Returns:
        Dict[str, Team]: Dictionary with all teams.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    uri = f'{api_url}/v1/c/{competition_id}/teams'

    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore
    teams: Dict[str, Team] = {}
    for item in response:
        team = _build_team(item)
        teams[team.participant_code] = team

    return teams


def update_driver(
        api_url: str,
        bearer: str,
        competition_id: int,
        driver_id: int,
        participant_code: str,
        name: str,
        number: int,
) -> Driver:
    """
    Update a driver.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        driver_id (int): ID of the driver.
        participant_code (str): Code of the driver.
        name (str): Name of the driver.
        number (int): Number of the driver.

    Returns:
        Driver: Updated driver instance.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }

    uri = f'{api_url}/v1/c/{competition_id}/drivers/{driver_id}'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_driver(response)


def update_team(
        api_url: str,
        bearer: str,
        competition_id: int,
        team_id: int,
        name: str,
        number: int,
        participant_code: str,
) -> Team:
    """
    Update a team.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        team_id (int): ID of the team.
        participant_code (str): Code of the team.
        name (str): Name of the team.
        number (int): Number of the team.

    Returns:
        Team: Updated team instance
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }
    uri = f'{api_url}/v1/c/{competition_id}/teams/{team_id}'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise LtsError(f'API unknown response: {response}')

    return _build_team(response)
