import re
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStatus,
    CompetitionInfo,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.parsers.base import Parser


class CompetitionMetadataStatusParser(Parser):
    """Parse the status of a competition (metadata)."""

    def __init__(self, competitions: Dict[str, CompetitionInfo]) -> None:
        """Construct."""
        self._competitions = competitions

    def parse(self, competition_code: str, data: Any) -> List[Action]:
        """
        Analyse and/or parse a given data.

        Params:
            competition_code (str): Code of the competition.
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
        """
        if competition_code not in self._competitions:
            raise Exception(f'Unknown competition with code={competition_code}')
        elif not isinstance(data, str):
            return []

        parsed_data = self._parse_metadata_status(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
            data=parsed_data,
        )
        return [action]

    def _parse_metadata_status(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateCompetitionMetadataStatus]:
        """Parse status of a competition."""
        data = data.strip()
        matches = re.match(r'^light\|(.+)\|$', data)
        if matches is None:
            return None

        raw_status = matches[1]
        if raw_status == 'lf':
            # Finished
            metadata = UpdateCompetitionMetadataStatus(
                competition_code=competition_code,
                status=CompetitionStatus.FINISHED,
            )
        elif raw_status == 'lg':
            # Started or on-going
            metadata = UpdateCompetitionMetadataStatus(
                competition_code=competition_code,
                status=CompetitionStatus.ONGOING,
            )
        elif raw_status == 'lr':
            # Paused
            metadata = UpdateCompetitionMetadataStatus(
                competition_code=competition_code,
                status=CompetitionStatus.PAUSED,
            )
        else:
            raise Exception(
                f'Unknown competition metadata status: {raw_status}')

        return metadata
