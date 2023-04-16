from enum import Enum
from pydantic import BaseModel as _BaseModel
from typing import Any, Dict, Tuple


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
