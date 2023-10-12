import pytest
from typing import Any, List

from ltspipe.data.actions import Action, ActionType
from ltspipe.data.competitions import (
    CompetitionInfo,
    CompetitionStage,
    Driver,
    KartStatus,
    Team,
    Timing,
    UpdateDriver,
    UpdateDriverPartialDrivingTime,
    UpdateTeam,
)
from ltspipe.data.enum import ParserSettings
from ltspipe.parsers.websocket.participants import (
    DriverNameParser,
    DriverPartialDrivingTimeParser,
    TeamNameParser,
)
from tests.fixtures import TEST_COMPETITION_CODE
from tests.helpers import load_raw_message

PARSERS_SETTINGS = {
    ParserSettings.TIMING_POSITION: 'c3',
    ParserSettings.TIMING_KART_NUMBER: 'c4',
    ParserSettings.TIMING_NAME: 'c5',
    ParserSettings.TIMING_LAST_TIME: 'c6',
    ParserSettings.TIMING_BEST_TIME: 'c7',
    ParserSettings.TIMING_GAP: 'c8',
    ParserSettings.TIMING_INTERVAL: 'c9',
    ParserSettings.TIMING_LAP: 'c10',
    ParserSettings.TIMING_PIT_TIME: 'c11',
    ParserSettings.TIMING_NUMBER_PITS: 'c12',
}


class TestDriverNameParser:
    """Test ltspipe.parsers.websocket.DriverNameParser."""

    @pytest.mark.parametrize(
        'info, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=None,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            partial_driving_time=None,
                            total_driving_time=None,
                            auto_compute_total=False,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_driver_name_with_driving_time.txt'),
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=None,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            partial_driving_time=67000,
                            total_driving_time=None,
                            auto_compute_total=False,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[
                        Driver(
                            id=3,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=3,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            partial_driving_time=None,
                            total_driving_time=None,
                            auto_compute_total=False,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[
                        Driver(
                            id=3,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_driver_name_with_driving_time.txt'),
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER,
                        data=UpdateDriver(
                            id=3,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='DIMAS MUNOZ',
                            number=41,
                            team_id=1,
                            partial_driving_time=67000,
                            total_driving_time=None,
                            auto_compute_total=False,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = DriverNameParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'info, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_driver_name.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = DriverNameParser(info=info)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestDriverPartialDrivingTimeParser:
    """Test ltspipe.parsers.websocket.DriverPartialDrivingTimeParser."""

    @pytest.mark.parametrize(
        'info, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[
                        Driver(
                            id=1,
                            participant_code='r5625',
                            name='Team 1 Driver 1',
                            number=41,
                            team_id=1,
                            total_driving_time=0,
                            partial_driving_time=0,
                        ),
                    ],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={
                        'r5625': Timing(
                            best_time=1,
                            driver_id=1,
                            fixed_kart_status=None,
                            gap=None,
                            interval=None,
                            kart_status=KartStatus.GOOD,
                            lap=3,
                            last_time=61000,
                            number_pits=2,
                            participant_code='r5625',
                            pit_time=0,
                            position=1,
                            stage=CompetitionStage.FREE_PRACTICE,
                            team_id=1,
                        ),
                    },
                ),
                load_raw_message(
                    'endurance_timing_driver_stint_time.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_DRIVER_PARTIAL_DRIVING_TIME,
                        data=UpdateDriverPartialDrivingTime(
                            id=1,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            partial_driving_time=70000,
                            auto_compute_total=False,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={},
                    timing={
                        'r5625': Timing(
                            best_time=1,
                            driver_id=None,
                            fixed_kart_status=None,
                            gap=None,
                            interval=None,
                            kart_status=KartStatus.GOOD,
                            lap=3,
                            last_time=61000,
                            number_pits=2,
                            participant_code='r5625',
                            pit_time=0,
                            position=1,
                            stage=CompetitionStage.FREE_PRACTICE,
                            team_id=1,
                        ),
                    },
                ),
                load_raw_message(
                    'endurance_timing_driver_stint_time.txt'),  # in_data
                [],  # expected_actions
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = DriverPartialDrivingTimeParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'info, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_timing_driver_stint_time.txt'),  # in_data
                'Unknown participant timing with code=r5625',
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = DriverPartialDrivingTimeParser(info=info)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception


class TestTeamNameParser:
    """Test ltspipe.parsers.websocket.TeamNameParser."""

    @pytest.mark.parametrize(
        'info, in_data, expected_actions, expected_is_parsed',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={
                        'r5625': Team(
                            id=1,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    },
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                [  # expected_actions
                    Action(
                        type=ActionType.UPDATE_TEAM,
                        data=UpdateTeam(
                            id=1,
                            competition_code=TEST_COMPETITION_CODE,
                            participant_code='r5625',
                            name='Team 1',
                            number=41,
                        ),
                    ),
                ],
                True,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                'unknown data input',  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings={},
                    drivers=[],
                    teams={},
                    timing={},
                ),
                ['unknown data format'],  # in_data
                [],  # expected_actions
                False,  # expected_is_parsed
            ),
        ],
    )
    def test_parse(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_actions: List[Action],
            expected_is_parsed: bool) -> None:
        """Test method parse with correct messages."""
        parser = TeamNameParser(info=info)
        out_actions, is_parsed = parser.parse(in_data)
        assert ([x.model_dump() for x in out_actions]
                == [x.model_dump() for x in expected_actions])
        assert is_parsed == expected_is_parsed

    @pytest.mark.parametrize(
        'info, in_data, expected_exception',
        [
            (
                CompetitionInfo(  # info
                    id=1,
                    competition_code=TEST_COMPETITION_CODE,
                    parser_settings=PARSERS_SETTINGS,
                    drivers=[],
                    teams={},
                    timing={},
                ),
                load_raw_message(
                    'endurance_display_team_name.txt'),  # in_data
                'Unknown team with code=r5625',  # expected_exception
            ),
        ],
    )
    def test_parse_raises_exception(
            self,
            info: CompetitionInfo,
            in_data: Any,
            expected_exception: str) -> None:
        """Test method parse with unexpected messages."""
        parser = TeamNameParser(info=info)
        with pytest.raises(Exception) as e_info:
            _ = parser.parse(in_data)
        e: Exception = e_info.value
        assert str(e) == expected_exception
