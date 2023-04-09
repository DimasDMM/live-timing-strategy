from pydantic import BaseModel


class IdFilter(BaseModel):
    """Filter by ID."""

    id: int


class CodeFilter(BaseModel):
    """Filter by code."""

    code: str


class NameFilter(BaseModel):
    """Filter by name."""

    name: str
