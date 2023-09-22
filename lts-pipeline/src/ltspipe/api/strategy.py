import requests

from ltspipe.data.strategy import StrategyPitsStats


def _build_strategy_pit_stats(raw: dict) -> StrategyPitsStats:
    """Build a pit-in instance from a dictionary."""
    ignore_keys = {'id', 'insert_date', 'update_date'}
    raw = {k: v for k, v in raw.items() if k not in ignore_keys}
    model: StrategyPitsStats = StrategyPitsStats.from_dict(raw)  # type: ignore
    return model


def add_strategy_pit_stats(
        api_url: str,
        bearer: str,
        competition_id: int,
        pit_in_id: int,
        best_time: int,
        avg_time: int) -> StrategyPitsStats:
    """
    Add a pit-in.

    Params:
        api_url (str): Base URL of the API REST.
        bearer (str): Bearer token.
        competition_id (int): ID of the competition.
        pit_in_id (int): ID of the last pit-in.
        best_time (int): Best time before the pit-in.
        avg_time (int): Average time before the pit-in.

    Returns:
        StrategyPitsStats: New strategy instance.
    """
    data = {
        'pit_in_id': pit_in_id,
        'best_time': best_time,
        'avg_time': avg_time,
    }

    uri = f'{api_url}/v1/c/{competition_id}/strategy/pits/stats'
    r = requests.post(
        url=uri, json=data, headers={'Authorization': f'Bearer {bearer}'})
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response: dict = r.json()  # type: ignore
    if 'id' not in response:
        raise Exception(f'API unknown response: {response}')

    return _build_strategy_pit_stats(response)  # type: ignore
