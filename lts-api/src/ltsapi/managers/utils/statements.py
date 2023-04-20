from pydantic import BaseModel
from typing import Callable, List, Optional, Union

from ltsapi.db import DBContext


def insert_model(
        db: DBContext,
        table_name: str,
        model: dict,
        commit: bool = True) -> Optional[int]:
    """
    Insert a model into the database.

    Params:
        db (DBContext): Connection to the database.
        table_name (str): Name of the table.
        model (dict): Model data as a dictionary.
        commit (bool): Do commit after insert.

    Returns:
        int | None: ID of inserted model.
    """
    fields = {k: v for k, v in model.items() if v is not None}
    headers, params = list(fields.keys()), list(fields.values())
    placeholders = ', '.join(['%s'] * len(headers))
    stmt_head = ', '.join([f'`{h}`' for h in headers])
    stmt = f'''
        INSERT INTO `{table_name}` ({stmt_head}) VALUES ({placeholders})'''
    cursor = db.get_cursor()
    try:
        cursor.execute(stmt, tuple(params))
        if commit:
            db.commit()
        return cursor.lastrowid
    except Exception as e:
        db.rollback()
        raise e


def update_model(
        db: DBContext,
        table_name: str,
        model: dict,
        key_name: Union[str, List[str]],
        key_value: Union[int, str, list],
        commit: bool = True) -> None:
    """Update the model in the database (as a dictionary)."""
    fields = {k: v for k, v in model.items()}
    stmt_fields, params = list(fields.keys()), list(fields.values())
    stmt_fields = [f'`{field}` = %s' for field in stmt_fields]

    if len(stmt_fields) > 0:
        if isinstance(key_name, list) and isinstance(key_value, list):
            # The key is complex
            stmt_where = [f'`{name}` = %s' for name in key_name]
            params += key_value
        else:
            stmt_where = [f'`{key_name}` = %s']
            params.append(key_value)

        stmt = f'''
            UPDATE `{table_name}` SET {",".join(stmt_fields)}
            WHERE {" AND ".join(stmt_where)}'''

        cursor = db.get_cursor()
        cursor.execute(stmt, tuple(params))
        if commit:
            db.commit()


def delete_model(
        db: DBContext,
        table_name: str,
        key_name: Union[str, List[str]],
        key_value: Union[int, str, list],
        commit: bool = True) -> None:
    """Delete a model from the database."""
    if isinstance(key_name, list) and isinstance(key_value, list):
        # The key is complex
        stmt_where = [f'`{name}` = %s' for name in key_name]
        params = key_value
    else:
        stmt_where = [f'`{key_name}` = %s']
        params = [key_value]

    stmt = f'DELETE FROM `{table_name}` WHERE {" AND ".join(stmt_where)}'

    cursor = db.get_cursor()
    cursor.execute(stmt, tuple(params))
    if commit:
        db.commit()


def fetchone_model(
        db: DBContext,
        model_factory: Callable[[dict], BaseModel],
        query: str,
        params: Optional[tuple] = None) -> Optional[BaseModel]:
    """
    Run the given query and retrieve a model.

    Params:
        db (DBContext): Connection with the database.
        model_factory (Callable): Function that creates the instance of the
            model given the results from the query.
        query (str): Query to run.
        params (tuple | None): If the query has any parameter, they should be
            provided through this argument.
    """
    cursor = db.get_cursor()
    cursor.execute(query, params)  # type: ignore
    raw_data: dict = cursor.fetchone()  # type: ignore
    return None if raw_data is None else model_factory(raw_data)


def fetchmany_models(
        db: DBContext,
        model_factory: Callable[[dict], BaseModel],
        query: str,
        params: Optional[tuple] = None) -> List[BaseModel]:
    """
    Run the given query and retrieve zero or many instances of the model.

    Params:
        db (DBContext): Connection with the database.
        model_factory (Callable): Function that creates the instance of the
            model given the results from the query.
        query (str): Query to run.
        params (tuple | None): If the query has any parameter, they should be
            provided through this argument.
    """
    cursor = db.get_cursor()
    cursor.execute(query, params)
    raw_data: List[dict] = cursor.fetchall()  # type: ignore
    items: List[BaseModel] = []
    for row in raw_data:
        items.append(model_factory(row))  # type: ignore
    return items
