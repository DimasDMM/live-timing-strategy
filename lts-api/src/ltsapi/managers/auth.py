import hashlib
from logging import Logger
import os
from time import time
from typing import Optional
import re

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    update_model,
    fetchone_model,
)
from ltsapi.models.enum import AuthRole
from ltsapi.models.auth import GetAuth, UpdateAuth, ValidateAuth


class AuthManager:
    """Manage the auth API data."""

    BASE_QUERY = '''
        SELECT
            api_auth.`bearer` AS auth_bearer,
            api_auth.`name` AS auth_name,
            api_auth.`role` AS auth_role
        FROM api_auth'''
    TABLE_NAME = 'api_auth'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger
        self._salt = os.environ.get('API_SALT')

    def get_by_key(self, key: str) -> Optional[GetAuth]:
        """
        Retrieve the auth data.

        Params:
            key (str): Auth key.

        Returns:
            GetAuth | None: Auth information.
        """
        query = f'{self.BASE_QUERY} WHERE api_auth.`key` = %s'
        model: Optional[GetAuth] = fetchone_model(  # type: ignore
            self._db, self._raw_to_auth, query, params=(key,))
        return model

    def get_by_bearer(self, bearer: str) -> Optional[ValidateAuth]:
        """
        Retrieve the auth data.

        Params:
            bearer (str): Bearer token.

        Returns:
            ValidateAuth | None: Auth information.
        """
        if not re.match('^Bearer .+', bearer):
            return None

        bearer = re.sub('^Bearer ', '', bearer)

        query = f'{self.BASE_QUERY} WHERE api_auth.`bearer` = %s'
        model: Optional[GetAuth] = fetchone_model(  # type: ignore
            self._db, self._raw_to_validation, query, params=(bearer,))
        return self._get_auth_to_validate_auth(model)

    def refresh_bearer(
            self, key: str, commit: bool = True) -> GetAuth:
        """
        Create a new bearer token.

        Params:
            key (str): Auth key.
            commit (bool): Commit transaction.

        Returns:
            GetAuth: Auth information.
        """
        model = self.get_by_key(key)
        if model is None:
            raise ApiError('Invalid API key.', status_code=401)

        # Do not update bearer token if the role is batch and the bearer token
        # is already set
        if (model.role == AuthRole.BATCH
                and model.bearer is not None
                and model.bearer != ''):
            return model

        new_model = UpdateAuth(
            bearer=self._generate_bearer(key),
            name=model.name,
            role=model.role,
        )
        update_model(
            self._db,
            self.TABLE_NAME,
            new_model.dict(),
            key_name='key',
            key_value=key,
            commit=commit)

        model.bearer = new_model.bearer
        return model

    def _get_auth_to_validate_auth(
            self,
            model: Optional[GetAuth]) -> Optional[ValidateAuth]:
        """Transform into a ValidateAuth instance."""
        if model is None:
            return None
        return ValidateAuth(
            name=model.name,
            role=model.role,
        )

    def _generate_bearer(self, key: str) -> str:
        """Generate bearer token from an API key."""
        str_encoded = str.encode(f'{self._salt}_{key}_{str(time())}')
        return hashlib.sha256(str_encoded).hexdigest()

    def _raw_to_auth(self, row: dict) -> GetAuth:
        """Build an instance of GetAuth."""
        return GetAuth(
            bearer=row['auth_bearer'],
            name=row['auth_name'],
            role=row['auth_role'],
        )

    def _raw_to_validation(self, row: dict) -> ValidateAuth:
        """Build an instance of ValidateAuth."""
        return ValidateAuth(
            name=row['auth_name'],
            role=row['auth_role'],
        )
