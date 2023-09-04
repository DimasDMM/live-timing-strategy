import re
from typing import Any, Dict, List, Optional

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStatus,
    CompetitionInfo,
    LengthUnit,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.parsers.base import Parser


class CompetitionMetadataRemainingParser(Parser):
    """
    Parse the remaining length of a competition (metadata).

    Sample messages:
    > dyn1|text|00:20:00
    > dyn1|countdown|10761515
    """

    # The following regex matches the following samples:
    # > '2:12.283'
    # > '00:20:00'
    # > '54.'
    REGEX_TIME = r'^\+?(?:(?:(\d+):)?(\d+):)?(\d+)(?:\.(\d+)?)?$'

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
        if not isinstance(data, str):
            return []

        parsed_data = self._parse_metadata_remaining(competition_code, data)
        if parsed_data is None:
            return []

        action = Action(
            type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,
            data=parsed_data,
        )
        return [action]

    def _parse_metadata_remaining(
            self,
            competition_code: str,
            data: str) -> Optional[UpdateCompetitionMetadataRemaining]:
        """Parse remaining length of a competition."""
        data = data.strip()
        matches = re.match(r'^dyn1\|(.+?)\|(.*)$', data)
        if matches is None:
            return None

        remaining_length_value = matches[2]
        if remaining_length_value.strip() == '':
            remaining_length_value = 0

        if matches[1] == 'countdown':
            return UpdateCompetitionMetadataRemaining(
                competition_code=competition_code,
                remaining_length={
                    'value': int(remaining_length_value),
                    'unit': LengthUnit.MILLIS,
                },
            )
        elif matches[1] == 'text':
            return UpdateCompetitionMetadataRemaining(
                competition_code=competition_code,
                remaining_length={
                    'value': self._time_to_millis(remaining_length_value),
                    'unit': LengthUnit.MILLIS,
                },
            )
        else:
            raise Exception(
                f'Unknown competition metadata remaining length: {data}')

    def _time_to_millis(
            self,
            lap_time: str,
            default: int = 0) -> Optional[int]:
        """Transform a lap time into milliseconds."""
        lap_time = lap_time.strip()
        match = re.search(self.REGEX_TIME, lap_time)
        if match is None:
            return default
        else:
            parts = [int(p) if p else 0 for p in match.groups()]
            return (parts[0] * 3600000
                + parts[1] * 60000
                + parts[2] * 1000
                + parts[3])


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
        if not isinstance(data, str):
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
