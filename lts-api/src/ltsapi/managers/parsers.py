from logging import Logger
from typing import List, Optional

from ltsapi.db import DBContext
from ltsapi.exceptions import ApiError
from ltsapi.managers.utils.statements import (
    insert_model,
    update_model,
    delete_model,
    fetchmany_models,
    fetchone_model,
)
from ltsapi.models.parsers import (
    AddParserSetting,
    GetParserSetting,
    UpdateParserSetting,
)


class ParsersSettingsManager:
    """Manage the settings of the parsers."""

    BASE_QUERY = '''
        SELECT
            ps.`name` AS ps_name,
            ps.`value` AS ps_value,
            ps.`insert_date` AS ps_insert_date,
            ps.`update_date` AS ps_update_date
        FROM parsers_settings AS ps'''
    TABLE_NAME = 'parsers_settings'

    def __init__(self, db: DBContext, logger: Logger) -> None:
        """Construct."""
        self._db = db
        self._logger = logger

    def get_by_name(
            self,
            setting_name: str,
            competition_id: int) -> Optional[GetParserSetting]:
        """
        Retrieve a setting by its name.

        Params:
            setting_name (str): Name of the setting.
            competition_id (int): ID of the competition.

        Returns:
            GetParserSetting | None: If the setting exist, it returns
                its instance.
        """
        query = f'''{self.BASE_QUERY}
                    WHERE ps.name = %s AND ps.competition_id = %s'''
        params = (setting_name, competition_id)
        model: Optional[GetParserSetting] = fetchone_model(  # type: ignore
            self._db, self._raw_to_setting, query, params=params)
        return model

    def get_by_competition(
            self, competition_id: int) -> List[GetParserSetting]:
        """
        Retrieve settings by competition.

        Params:
            competition_id (int): ID of the competition.

        Returns:
            List[GetParserSetting]: List of settings.
        """
        query = f'{self.BASE_QUERY} WHERE ps.competition_id = %s'
        models: List[GetParserSetting] = fetchmany_models(  # type: ignore
            self._db, self._raw_to_setting, query, params=(competition_id,))
        return models

    def add_one(
            self,
            setting: AddParserSetting,
            competition_id: int,
            commit: bool = True) -> Optional[int]:
        """
        Add a new setting.

        Params:
            setting (AddParserSetting): Data of the setting.
            competition_id (int): ID of the competition.
            commit (bool): Commit transaction.

        Returns:
            int | None: ID of inserted model.
        """
        if self._exists_by_name(setting.name, competition_id):
            raise ApiError(
                message=f'The setting "{setting.name}" '
                        f'(competition={competition_id}) already exists.',
                status_code=400)

        model_data = setting.dict()
        model_data['competition_id'] = competition_id
        item_id = insert_model(
            self._db, self.TABLE_NAME, model_data, commit=commit)
        return item_id

    def update_by_name(
            self,
            setting: UpdateParserSetting,
            setting_name: str,
            competition_id: int,
            commit: bool = True) -> None:
        """
        Update the data of a setting (it must already exist).

        Params:
            setting (UpdateParserSetting): New data of the
                setting ('None' is ignored).
            setting_name (name): Name of the setting.
            competition_id (int | None): ID of the competition.
            commit (bool): Commit transaction.
        """
        if self._exists_by_name(setting_name, competition_id) is None:
            raise ApiError(
                message=f'The setting with ID={setting_name} does not exist.',
                status_code=400)
        key_name = ['name', 'competition_id']
        key_value = [setting_name, competition_id]
        update_model(
            self._db,
            self.TABLE_NAME,
            setting.dict(),
            key_name=key_name,
            key_value=key_value,
            commit=commit)

    def delete_by_competition(
            self,
            competition_id: int,
            commit: bool = True) -> None:
        """
        Delete the parsers settings of a competition.

        Params:
            competition_id (int | None): ID of the competition.
            commit (bool): Commit transaction.
        """
        delete_model(
            self._db,
            self.TABLE_NAME,
            key_name='competition_id',
            key_value=competition_id,
            commit=commit)

    def _exists_by_name(
            self, setting_name: str, competition_id: int) -> bool:
        """Check if a team with the given code exists."""
        model = self.get_by_name(setting_name, competition_id)
        return model is not None

    def _raw_to_setting(self, row: dict) -> GetParserSetting:
        """Build an instance of GetParserSetting."""
        return GetParserSetting(
            name=row['ps_name'],
            value=row['ps_value'],
            insert_date=row['ps_insert_date'],
            update_date=row['ps_update_date'],
        )
