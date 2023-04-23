import requests

from ltspipe.data.auth import AuthData


def refresh_bearer(
        api_url: str,
        key: str) -> AuthData:
    """Do authentication."""
    uri = (f'{api_url}/v1/auth')
    data = {'key': key}
    r = requests.post(url=uri, json=data)
    if r.status_code != 200:
        raise Exception(f'API error: {r.text}')

    response = r.json()
    auth_data: AuthData = AuthData.from_dict(response)  # type: ignore
    return auth_data
