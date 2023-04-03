from ltspipe.data.time import DiffLap, Unit


class TestDiffLap:
    """Test ltspipe.data.time.DiffLap."""

    def test_to_dict(self) -> None:
        """Test to_dict method."""
        diff_lap = DiffLap(value=10, unit=Unit.LAPS)
        expected = {'value': 10, 'unit': 'laps'}
        assert dict(diff_lap.to_dict()) == expected
