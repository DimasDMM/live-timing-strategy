from typing import Optional

from ltsapi.models import BaseModel


class GetAuth(BaseModel):
    """Auth data."""

    bearer: Optional[str]
    name: str
    role: str


class SendAuthKey(BaseModel):
    """Send auth key."""

    key: str


class UpdateAuth(BaseModel):
    """Update the auth data."""

    bearer: Optional[str]
    name: str
    role: str
