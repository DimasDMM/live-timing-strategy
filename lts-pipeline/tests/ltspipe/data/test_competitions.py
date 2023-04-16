from ltspipe.data.competitions import DiffLap
from ltspipe.data.enum import LengthUnit


class TestDiffLap:
    """Test ltspipe.data.competitions.DiffLap."""

    def test_dict(self) -> None:
        """Test dict method."""
        diff_lap = DiffLap(value=10, unit=LengthUnit.LAPS)
        expected = {'value': 10, 'unit': 'laps'}
        assert dict(diff_lap.dict()) == expected
