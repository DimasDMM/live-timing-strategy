from abc import ABC, abstractmethod
from enum import Enum
from pydantic import BaseModel as _BaseModel
from typing import Any, Dict, Tuple


class EnumBase(Enum):
    """Enumeration that allows comparison."""

    def __eq__(self, other: Any) -> bool:
        """Compare enumeration to other objects and strings."""
        if self.__class__ is other.__class__:
            return self.value == other.value
        elif isinstance(other, str):
            return self.value == other
        return False

    def __hash__(self) -> int:
        """Build hash of current instance."""
        return hash(self.value)

    @classmethod
    def value_of(cls: Any, value: Any) -> Any:
        """Build source message from a given value."""
        for k, v in cls.__members__.items():
            if cls[k] == value:
                return v
        raise ValueError(f'"{cls.__name__}" enum not found for "{value}".')


class BaseModel(_BaseModel):
    """Base class for data models."""

    def dict(self,  # type: ignore
             *args: Tuple[Any, ...],
             **kwargs: Dict[Any, Any]) -> Dict[Any, Any]:
        """Transform model into a dictionary."""
        data = super().dict(*args, **kwargs)  # type: ignore
        for field_name, field_value in data.items():
            if field_value is not None and isinstance(field_value, Enum):
                data[field_name] = field_value.value
        return data


class DictModel(BaseModel, ABC):
    """Base class to load models from dictionaries."""

    @classmethod
    @abstractmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        raise NotImplementedError

    @staticmethod
    def _validate_base_dict(
            cls: BaseModel,
            raw: dict,
            ignore_unknowns: bool = False) -> None:  # noqa: ANN102
        """Do a basic validation on the raw data."""
        for field_name, field_props in cls.__fields__.items():
            if field_props.required and field_name not in raw:
                raise Exception(f'Missing required field: {field_name}')

        if not ignore_unknowns:
            fields = set(cls.__fields__.keys())
            raw_fields = set(raw)
            if raw_fields.intersection(fields) != raw_fields:
                raise Exception(f'There are unknown fields: {raw_fields}')
