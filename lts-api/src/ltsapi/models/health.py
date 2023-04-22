from ltsapi.models import BaseModel


class GetHealth(BaseModel):
    """API health status."""

    status: str
