from ltspipe.data.base import BaseModel
from ltspipe.data.base import DictModel


class AddStrategyPitsStats(DictModel):
    """Info of a strategy pits stats."""

    pit_in_id: int
    best_time: int
    avg_time: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            pit_in_id=raw.get('pit_in_id'),
            best_time=raw.get('best_time'),
            avg_time=raw.get('avg_time'),
        )


class StrategyPitsStats(DictModel):
    """Info of a strategy pits stats."""

    pit_in_id: int
    best_time: int
    avg_time: int

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.model_construct(
            pit_in_id=raw.get('pit_in_id'),
            best_time=raw.get('best_time'),
            avg_time=raw.get('avg_time'),
        )
