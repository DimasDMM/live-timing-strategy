import requests
from typing import List, Optional

from ltspipe.data.competitions import (
    Driver,
    Team,
)


def add_driver(
        api_url: str,
        competition_id: int,
        participant_code: str,
        name: str,
        number: int,
        team_id: Optional[int] = None) -> int:
    """
    Add a new driver.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        participant_code (str): Code of the driver.
        name (str): Name of the driver.
        number (int): Number of the driver.
        team_id (int | None): ID of the team if there is any.

    Returns:
        int: ID of the new driver.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }

    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/competitions/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers'

    r = requests.post(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return response['id']


def add_team(
        api_url: str,
        competition_id: int,
        participant_code: str,
        name: str,
        number: int) -> int:
    """
    Add a new team.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        participant_code (str): Code of the team.
        name (str): Name of the team.
        number (int): Number of the team.

    Returns:
        int: ID of the new team.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
    }
    uri = f'{api_url}/v1/competitions/{competition_id}/teams'
    r = requests.post(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return response['id']


def get_driver(
        api_url: str,
        competition_id: int,
        driver_id: int,
        team_id: Optional[int] = None) -> Optional[Driver]:
    """
    Get a single driver.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        driver_id (int): ID of the driver.
        team_id (int | None): ID of the team if there is any.

    Returns:
        Optional[Driver]: Instance of the driver.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/competitions/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers/{driver_id}'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers/{driver_id}'

    r = requests.get(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    allowed_keys = {'id', 'participant_code', 'name', 'number', 'team_id'}
    response = {k: v for k, v in response.items() if k in allowed_keys}
    driver: Driver = Driver.from_dict(response)  # type: ignore

    return driver


def get_team(
        api_url: str,
        competition_id: int,
        team_id: int) -> Optional[Team]:
    """
    Get a single team.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        team_id (int): ID of the team.

    Returns:
        Optional[Team]: Instance of the team.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    uri = f'{api_url}/v1/competitions/{competition_id}/teams/{team_id}'

    r = requests.get(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        return None

    allowed_keys = {'id', 'participant_code', 'name', 'number'}
    response = {k: v for k, v in response.items() if k in allowed_keys}
    team: Team = Team.from_dict(response)  # type: ignore

    return team


def get_all_drivers(
        api_url: str,
        competition_id: int,
        team_id: Optional[int] = None) -> List[Driver]:
    """
    Get all drivers.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        team_id (int | None): ID of the team if there is any.

    Returns:
        List[Driver]: List of drivers.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/competitions/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers'

    r = requests.get(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore

    allowed_keys = {'id', 'participant_code', 'name', 'number', 'team_id'}
    drivers: List[Driver] = []
    for item in response:
        item = {k: v for k, v in item.items() if k in allowed_keys}
        drivers.append(Driver.from_dict(item))  # type: ignore

    return drivers


def get_all_teams(api_url: str, competition_id: int) -> List[Team]:
    """
    Get all teams.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.

    Returns:
        List[Team]: List of teams.
    """
    # Depending on there is a team or not, the endpoint is slightly different
    uri = f'{api_url}/v1/competitions/{competition_id}/teams'

    r = requests.get(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: List[dict] = r.json()  # type: ignore

    allowed_keys = {'id', 'participant_code', 'name', 'number'}
    teams: List[Team] = []
    for item in response:
        item = {k: v for k, v in item.items() if k in allowed_keys}
        teams.append(Team.from_dict(item))  # type: ignore

    return teams


def update_driver(
        api_url: str,
        competition_id: int,
        driver_id: int,
        participant_code: str,
        name: str,
        number: int,
        total_driving_time: int,
        partial_driving_time: int,
        reference_time_offset: Optional[int] = None,
        team_id: Optional[int] = None,
) -> int:
    """
    Update a driver.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        driver_id (int): ID of the driver.
        participant_code (str): Code of the driver.
        name (str): Name of the driver.
        number (int): Number of the driver.
        total_driving_time (int): Total driving time.
        partial_driving_time (int): Partial driving time.
        reference_time_offset (int | None): Offset of time reference.
        team_id (int | None): ID of the team if there is any.

    Returns:
        int: ID of the new driver.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
        'total_driving_time': total_driving_time,
        'partial_driving_time': partial_driving_time,
        'reference_time_offset': reference_time_offset,
    }

    # Depending on there is a team or not, the endpoint is slightly different
    url_prefix = f'{api_url}/v1/competitions/{competition_id}'
    if team_id is None:
        uri = f'{url_prefix}/drivers/{driver_id}'
    else:
        uri = f'{url_prefix}/teams/{team_id}/drivers/{driver_id}'

    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return response['id']


def update_team(
        api_url: str,
        competition_id: int,
        team_id: int,
        name: str,
        number: int,
        participant_code: str,
        reference_time_offset: Optional[int],
) -> int:
    """
    Update a team.

    Params:
        api_url (str): Base URL of the API REST.
        competition_id (int): ID of the competition.
        team_id (int): ID of the team.
        participant_code (str): Code of the team.
        name (str): Name of the team.
        number (int): Number of the team.
        reference_time_offset (int | None): Offset of time reference.

    Returns:
        int: ID of the new team.
    """
    data = {
        'participant_code': participant_code,
        'name': name,
        'number': number,
        'reference_time_offset': reference_time_offset,
    }
    uri = f'{api_url}/v1/competitions/{competition_id}/teams/{team_id}'
    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return response['id']
