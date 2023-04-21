from pydantic import BaseModel, Field


class Empty(BaseModel):
    """Empty model."""

    pass


class ErrorResponse(BaseModel):
    """Response with error details."""

    status_code: int
    message: str
    extra_data: dict = Field(default_factory=dict)
