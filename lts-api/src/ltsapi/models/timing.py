from pydantic import BaseModel


class UpdateReferenceTime(BaseModel):
    """Data to update a time."""

    id: int
    time: int
