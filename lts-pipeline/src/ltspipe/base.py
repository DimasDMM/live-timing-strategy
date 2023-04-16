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
