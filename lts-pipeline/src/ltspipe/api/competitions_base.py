import requests
from typing import Dict, Optional

from ltspipe.api.participants import (
    get_all_drivers,
    get_all_teams,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    CompetitionStatus,
)
from ltspipe.data.competitions import DiffLap


def init_competition_info(
        api_url: str,
        competition_code: str) -> CompetitionInfo:
    """
    Initialize information of competition.

    Note that this step is skipped if the information is already set.
    """
    uri = f'{api_url}/v1/competitions/filter/code/{competition_code}'
    r = requests.get(url=uri)
    response = r.json()

    if not response or 'id' not in response:
        raise Exception(f'Unknown API response ({uri}): {response}')

    competition_id = response['id']
    return CompetitionInfo(
        id=competition_id,
        competition_code=competition_code,
        parser_settings=get_parsers_settings(api_url, competition_id),
        drivers=get_all_drivers(api_url, competition_id, team_id=None),
        teams=get_all_teams(api_url, competition_id),
    )


def update_competition_metadata(
        api_url: str,
        competition_id: int,
        reference_time: Optional[int],
        reference_current_offset: Optional[int],
        status: Optional[CompetitionStatus],
        stage: Optional[CompetitionStage],
        remaining_length: Optional[DiffLap]) -> None:
    """Update the metadata of a competition."""
    data = {
        'reference_time': reference_time,
        'reference_current_offset': reference_current_offset,
        'status': None if status is None else status.value,
        'stage': None if stage is None else stage.value,
        'remaining_length': (None if remaining_length is None
                             else remaining_length.value),
        'remaining_length_unit': (None if remaining_length is None
                                  else remaining_length.unit.value),
    }
    uri = f'{api_url}/v1/competitions/{competition_id}/metadata'
    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')


def add_parsers_settings(
        api_url: str,
        competition_id: int,
        setting_name: ParserSettings,
        setting_value: str) -> None:
    """Add a new parsers settings."""
    uri = (f'{api_url}/v1/competitions/{competition_id}/parsers/settings')
    data = {
        'name': setting_name,
        'value': setting_value,
    }
    r = requests.post(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')


def delete_parsers_settings(
        api_url: str,
        competition_id: int) -> None:
    """Delete all the parsers settings of a competition."""
    uri = f'{api_url}/v1/competitions/{competition_id}/parsers/settings'
    r = requests.delete(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')


def get_parsers_settings(
        api_url: str,
        competition_id: int) -> Dict[ParserSettings, str]:
    """Get the parsers settings."""
    uri = f'{api_url}/v1/competitions/{competition_id}/parsers/settings'
    r = requests.get(url=uri)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, list):
        raise Exception(f'Unknown API response ({uri}): {response}')

    parser_settings: Dict[ParserSettings, str] = {}
    for item in response:
        if 'name' not in item or 'value' not in item:
            raise Exception(f'Unknown API response: {response}')
        parser_settings[ParserSettings.value_of(item['name'])] = item['value']

    return parser_settings


def update_parsers_settings(
        api_url: str,
        competition_id: int,
        setting_name: ParserSettings,
        setting_value: str) -> None:
    """Update the parsers settings."""
    uri = (f'{api_url}/v1/competitions/{competition_id}'
           f'/parsers/settings/{setting_name}')
    data = {'value': setting_value}
    r = requests.put(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')
