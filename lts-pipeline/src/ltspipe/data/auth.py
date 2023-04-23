from ltspipe.base import BaseModel, DictModel, EnumBase


class AuthRole(str, EnumBase):
    """Type of role."""

    ADMIN = 'admin'
    BATCH = 'batch'
    VIEWER = 'viewer'


class AuthData(DictModel):
    """Authentication data."""

    bearer: str
    name: str
    role: AuthRole

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        DictModel._validate_base_dict(cls, raw)  # type: ignore
        return cls.construct(
            bearer=raw.get('bearer'),
            name=raw.get('data'),
            role=AuthRole(raw.get('role')),
        )
