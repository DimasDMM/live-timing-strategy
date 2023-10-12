import re
from typing import Any, List, Optional, Tuple

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionStatus,
    CompetitionInfo,
    DiffLap,
    UpdateCompetitionMetadataRemaining,
    UpdateCompetitionMetadataStatus,
)
from ltspipe.data.enum import LengthUnit
from ltspipe.exceptions import LtsError
from ltspipe.parsers.base import Parser
from ltspipe.utils import time_to_millis


class CompetitionMetadataRemainingParser(Parser):
    """
    Parse the remaining length of a competition (metadata).

    Sample messages:
    > dyn1|text|00:20:00
    > dyn1|countdown|10761515
    """

    def __init__(self, info: CompetitionInfo) -> None:
        """Construct."""
        self._info = info

    def parse(
            self,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        if not isinstance(data, str):
            return [], False

        parsed_data = self._parse_metadata_remaining(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_COMPETITION_METADATA_REMAINING,
            data=parsed_data,
        )
        return [action], True

    def _parse_metadata_remaining(
            self,
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
                remaining_length=DiffLap(
                    value=int(remaining_length_value),
                    unit=LengthUnit.MILLIS,
                ),
            )
        elif matches[1] == 'text':
            return UpdateCompetitionMetadataRemaining(
                remaining_length=DiffLap(
                    value=time_to_millis(  # type: ignore
                        remaining_length_value, default=0),
                    unit=LengthUnit.MILLIS,
                ),
            )
        else:
            raise LtsError(
                f'Unknown competition metadata remaining length: {data}')


class CompetitionMetadataStatusParser(Parser):
    """Parse the status of a competition (metadata)."""

    def __init__(self, info: CompetitionInfo) -> None:
        """Construct."""
        self._info = info

    def parse(
            self,
            data: Any) -> Tuple[List[Action], bool]:
        """
        Analyse and/or parse a given data.

        Params:
            data (Any): Data to parse.

        Returns:
            List[Action]: list of actions and their respective parsed data.
            bool: indicates whether the data has been parsed or not.
        """
        if not isinstance(data, str):
            return [], False

        parsed_data = self._parse_metadata_status(data)
        if parsed_data is None:
            return [], False

        action = Action(
            type=ActionType.UPDATE_COMPETITION_METADATA_STATUS,
            data=parsed_data,
        )
        return [action], True

    def _parse_metadata_status(
            self,
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
                status=CompetitionStatus.FINISHED,
            )
        elif raw_status == 'lg':
            # Started or on-going
            metadata = UpdateCompetitionMetadataStatus(
                status=CompetitionStatus.ONGOING,
            )
        elif raw_status == 'lr':
            # Paused
            metadata = UpdateCompetitionMetadataStatus(
                status=CompetitionStatus.PAUSED,
            )
        else:
            raise LtsError(
                f'Unknown competition metadata status: {raw_status}')

        return metadata
