from logging import Logger
import requests
from typing import Any, Dict, List, Optional

from ltspipe.data.competitions import CompetitionInfo
from ltspipe.messages import Message
from ltspipe.steps.base import MidStep


class ApiParserSettingsStep(MidStep):
    """Retrieve the parser settings."""

    def __init__(
            self,
            logger: Logger,
            api_lts: str,
            competitions: Optional[Dict[str, CompetitionInfo]] = None,
            next_step: Optional[MidStep] = None) -> None:
        """
        Construct.

        Params:
            logger (logging.Logger): Logger instance to display information.
            api_lts (str): URI of API REST.
            competitions (Dict[str, CompetitionInfo] | None): Storage of
                competitions info.
            next_step (MidStep | None): Next step.
        """
        self._logger = logger
        self._api_lts = api_lts.strip('/')
        self._competitions = {} if competitions is None else competitions
        self._next_step = next_step

    def get_children(self) -> List[Any]:
        """Return list of children steps to this one."""
        if self._next_step is None:
            return []
        else:
            return [self._next_step] + self._next_step.get_children()

    def run_step(self, msg: Message) -> None:
        """Update parsers settings of the competition."""
        self._update_settings(msg.competition_code)
        if self._next_step is not None:
            self._next_step.run_step(msg)

    def _update_settings(self, competition_code: str) -> None:
        """Update the parsers settings."""
        if (competition_code not in self._competitions
                or self._competitions[competition_code].id is None):
            self._init_competition_settings(competition_code)

        info = self._competitions[competition_code]
        competition_id: int = info.id  # type: ignore
        uri = self._settings_endpoint(competition_id)
        r = requests.get(url=uri)
        response = r.json()

        if not response or not isinstance(response, list):
            raise Exception(f'Unknown API response ({uri}): {response}')

        for item in response:
            if 'name' not in item or 'value' not in item:
                raise Exception(f'Unknown API response: {response}')
            info.parser_settings[item['name']] = item['value']

    def _init_competition_settings(self, competition_code: str) -> None:
        """Initialize information of competition."""
        uri = self._index_endpoint(competition_code)
        r = requests.get(url=uri)
        response = r.json()

        if competition_code not in self._competitions:
            info = CompetitionInfo(competition_code=competition_code)
            self._competitions[competition_code] = info
        else:
            info = self._competitions[competition_code]

        if not response or 'id' not in response:
            raise Exception(f'Unknown API response ({uri}): {response}')

        info.id = response['id']

    def _index_endpoint(self, competition_code: str) -> str:
        """Get endpoint of parsers settings."""
        base = self._api_lts
        return f'{base}/v1/competitions/filter/code/{competition_code}'

    def _settings_endpoint(self, competition_id: int) -> str:
        """Get endpoint of parsers settings."""
        base = self._api_lts
        return f'{base}/v1/competitions/{competition_id}/parsers/settings'
