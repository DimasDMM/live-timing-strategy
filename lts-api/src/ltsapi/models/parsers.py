from datetime import datetime

from ltsapi.models import BaseModel


class AddParserSetting(BaseModel):
    """Setting of a parser."""

    name: str
    value: str


class GetParserSetting(BaseModel):
    """Setting of a parser."""

    name: str
    value: str
    insert_date: datetime
    update_date: datetime


class UpdateParserSetting(BaseModel):
    """Data to update the value of a setting."""

    value: str
