import requests
from typing import Dict

from ltspipe.api.participants import (
    get_all_drivers,
    get_all_teams,
)
from ltspipe.api.timing import get_all_timing
from ltspipe.data.enum import ParserSettings
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionMetadata,
    CompetitionStage,
    CompetitionStatus,
)
from ltspipe.data.competitions import DiffLap
from ltspipe.exceptions import LtsError


def _build_competition_metadata(raw: dict) -> CompetitionMetadata:
    """Build a driver instance from a dictionary."""
    ignore_keys = {'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    return CompetitionMetadata.from_dict(raw)  # type: ignore


def build_competition_info(
        api_url: str,
        bearer: str,
        competition_code: str) -> CompetitionInfo:
    """
    Initialize information of competition.

    Note that this step is skipped if the information is already set.
    """
    uri = f'{api_url}/v1/c/filter/code/{competition_code}'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    response = r.json()

    if not response or 'id' not in response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    competition_id = response['id']
    parser_settings = get_parsers_settings(api_url, bearer, competition_id)
    drivers = get_all_drivers(api_url, bearer, competition_id, team_id=None)
    teams = get_all_teams(api_url, bearer, competition_id)
    timing = get_all_timing(api_url, bearer, competition_id)

    return CompetitionInfo(
        id=competition_id,
        competition_code=competition_code,
        parser_settings=parser_settings,
        drivers=drivers,
        teams=teams,
        timing=timing,
    )


def get_competition_metadata(
        api_url: str,
        bearer: str,
        competition_id: int) -> CompetitionMetadata:
    """Get the metadata of a competition."""
    uri = f'{api_url}/v1/c/{competition_id}/metadata'
    r = requests.get(
        url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if not response:
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return _build_competition_metadata(response)


def update_competition_metadata(
        api_url: str,
        bearer: str,
        competition_id: int,
        status: CompetitionStatus,
        stage: CompetitionStage,
        remaining_length: DiffLap) -> None:
    """Update the metadata of a competition."""
    data = {
        'status': status.value,
        'stage': stage.value,
        'remaining_length': remaining_length.value,
        'remaining_length_unit': remaining_length.unit.value,
    }
    uri = f'{api_url}/v1/c/{competition_id}/metadata'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')


def update_competition_metadata_remaining(
        api_url: str,
        bearer: str,
        competition_id: int,
        remaining_length: DiffLap) -> CompetitionMetadata:
    """Update the remaining length of a competition metadata."""
    data = {
        'remaining_length': remaining_length.value,
        'remaining_length_unit': remaining_length.unit,
    }
    uri = f'{api_url}/v1/c/{competition_id}/metadata/remaining_length'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, dict):
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return _build_competition_metadata(response)


def update_competition_metadata_status(
        api_url: str,
        bearer: str,
        competition_id: int,
        status: CompetitionStatus) -> CompetitionMetadata:
    """Update the status of a competition metadata."""
    data = {
        'status': status.value,
    }
    uri = f'{api_url}/v1/c/{competition_id}/metadata/status'
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, dict):
        raise LtsError(f'Unknown API response ({uri}): {response}')

    return _build_competition_metadata(response)


def add_parsers_settings(
        api_url: str,
        bearer: str,
        competition_id: int,
        setting_name: ParserSettings,
        setting_value: str) -> None:
    """Add a new parsers settings."""
    uri = (f'{api_url}/v1/c/{competition_id}/parsers/settings')
    data = {
        'name': setting_name,
        'value': setting_value,
    }
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')


def delete_parsers_settings(
        api_url: str,
        bearer: str,
        competition_id: int) -> None:
    """Delete all the parsers settings of a competition."""
    uri = f'{api_url}/v1/c/{competition_id}/parsers/settings'
    r = requests.delete(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')


def get_parsers_settings(
        api_url: str,
        bearer: str,
        competition_id: int) -> Dict[ParserSettings, str]:
    """Get the parsers settings."""
    uri = f'{api_url}/v1/c/{competition_id}/parsers/settings'
    r = requests.get(url=uri, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')

    response = r.json()
    if not isinstance(response, list):
        raise LtsError(f'Unknown API response ({uri}): {response}')

    parser_settings: Dict[ParserSettings, str] = {}
    for item in response:
        if 'name' not in item or 'value' not in item:
            raise LtsError(f'Unknown API response: {response}')
        parser_settings[ParserSettings.value_of(item['name'])] = item['value']

    return parser_settings


def update_parsers_settings(
        api_url: str,
        bearer: str,
        competition_id: int,
        setting_name: ParserSettings,
        setting_value: str) -> None:
    """Update the parsers settings."""
    uri = (f'{api_url}/v1/c/{competition_id}'
           f'/parsers/settings/{setting_name}')
    data = {'value': setting_value}
    r = requests.put(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise LtsError(f'API error: {r.text}')
