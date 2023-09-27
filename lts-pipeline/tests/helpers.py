from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
import os
import pathlib
from pydantic import BaseModel
import requests
from typing import Any, List, Optional, Tuple
from unittest.mock import MagicMock

from ltspipe.base import BaseModel, DictModel
from ltspipe.data.actions import Action, ActionType
from ltspipe.data.enum import LengthUnit
from ltspipe.parsers.base import Parser
from tests.fixtures import TEST_COMPETITION_CODE

BASE_PATH = 'tests/data/messages'


class DummyParser(Parser):
    """Dummy parser."""

    def parse(
        self,
        competition_code: str,  # noqa: U100
        data: Any,  # noqa: U100
    ) -> Tuple[List[Action], bool]:
        """Parse dummy."""
        return [], True


class DummyModel(DictModel):
    """dummy data."""

    text: Optional[str]

    @classmethod
    def from_dict(cls, raw: dict) -> BaseModel:  # noqa: ANN102
        """Return an instance of itself with the data in the dictionary."""
        return cls.model_construct(
            text=raw.get('text', None),
        )


def build_magic_step() -> MagicMock:
    """Create mock of a step."""
    step = MagicMock()
    step.get_children.return_value = []
    return step


def build_magic_parser() -> Tuple[DummyParser, MagicMock]:
    """Create mock of a parser."""
    mocked = MagicMock(return_value=(
        [Action(type=ActionType.INITIALIZE, data=DummyModel(text=None))], True))
    parser = DummyParser()
    parser.parse = mocked  # type: ignore
    return parser, mocked


def load_raw_message(filename: str) -> str:
    """Load a raw message."""
    filepath = os.path.join(BASE_PATH, filename)
    with open(filepath, 'r') as fp:
        return fp.read()


class TableQuery(BaseModel):
    """Query to a database table."""

    table_name: str
    columns: List[str]


class DatabaseQuery(BaseModel):
    """Query to the database."""

    tables_query: List[TableQuery]


class TableContent(BaseModel):
    """Content of a database table."""

    table_name: str
    columns: List[str]
    content: list


class DatabaseContent(BaseModel):
    """Content of the database."""

    tables_content: List[TableContent]

    def to_query(self) -> DatabaseQuery:
        """Transform into a DatabaseQuery instance."""
        tables_query: List[TableQuery] = []
        for t in self.tables_content:
            tables_query.append(
                TableQuery(table_name=t.table_name, columns=t.columns))
        return DatabaseQuery(tables_query=tables_query)


class DatabaseTest:
    """
    Initialize a database to run the functional tests.

    Note that this class creates a new database on each class-level run and,
    once the tests have finished, it resets its schema and content.
    """

    DATABASE_NAME = os.environ.get('DB_DATABASE')
    INIT_DATA_FILE = '../lts-api/data/init.sql'
    SCHEMA_FILE = '../lts-api/data/schema.sql'

    def setup_method(self, method: Any) -> None:  # noqa: U100
        """Set up."""
        DatabaseTest.reset_database()

    def teardown_method(self, method: Any) -> None:  # noqa: U100
        """Reset state of the database."""
        pass

    def set_database_content(self, database: DatabaseContent) -> None:
        """Set content of the database."""
        cnx, cursor = DatabaseTest._build_db_connection(use_database=True)
        for table in database.tables_content:
            for row in table.content:
                DatabaseTest._insert_model(
                    cnx, cursor, table.table_name, table.columns, row)
        cnx.commit()

    def get_database_content(
            self,
            database_query: DatabaseQuery) -> DatabaseContent:
        """Get content from the database."""
        _, cursor = DatabaseTest._build_db_connection(use_database=True)

        tables_content: List[TableContent] = []
        for table in database_query.tables_query:
            t = DatabaseTest._query_models(
                cursor, table.table_name, table.columns)
            tables_content.append(t)

        return DatabaseContent(tables_content=tables_content)

    @staticmethod
    def reset_database() -> None:
        """Reset (remove and create) the database."""
        cnx, cursor = DatabaseTest._build_db_connection()
        DatabaseTest._drop_database(cnx, cursor)
        DatabaseTest._init_database(cnx, cursor)
        cursor.close()
        cnx.close()

    @staticmethod
    def _build_db_connection(
            use_database: bool = False) -> Tuple[MySQLConnection, MySQLCursor]:
        """Build connection with the database."""
        cnx = MySQLConnection(
            host=os.environ.get('DB_HOST', None),
            port=os.environ.get('DB_PORT', None),
            user=os.environ.get('DB_USER', None),
            password=os.environ.get('DB_PASS', None))
        cnx.autocommit = False
        cursor = cnx.cursor()
        cursor.execute('SET NAMES "utf8";')
        if use_database:
            cursor.execute(f'USE `{DatabaseTest.DATABASE_NAME}`')
        return cnx, cursor

    @staticmethod
    def _insert_model(
            cnx: MySQLConnection,
            cursor: MySQLCursor,
            table_name: str,
            columns: List[str],
            row: list) -> Optional[int]:
        """
        Insert a row into the database.

        Params:
            cnx (MySQLConnection): Connection to the database.
            cursor (MySQLCursor): Connection cursor.
            table_name (str): Name of the table.
            columns (List[str]): List of columns
            row (list): Row data.

        Returns:
            int | None: ID of inserted row.
        """
        fields = {k: v for k, v in zip(columns, row) if v is not None}
        headers, params = list(fields.keys()), list(fields.values())
        placeholders = ', '.join(['%s'] * len(headers))
        stmt_head = ', '.join([f'`{h}`' for h in headers])
        stmt = f'''
            INSERT INTO `{table_name}` ({stmt_head}) VALUES ({placeholders})'''
        try:
            cursor.execute(stmt, tuple(params))
            return cursor.lastrowid
        except Exception as e:
            cnx.rollback()
            raise e

    @staticmethod
    def _query_models(
            cursor: MySQLCursor,
            table_name: str,
            columns: List[str]) -> DatabaseContent:
        """
        Run the given query and retrieve zero or many instances of the model.

        Params:
            cnx (MySQLConnection): Connection to the database.
            cursor (MySQLCursor): Connection cursor.
            table_name (str): Name of the table.
            columns (List[str]): List of columns to retrieve.

        Returns:
            TableContent: Content of the table.
        """
        columns_str = ', '.join([f'`{c}`' for c in columns])
        query = f'SELECT {columns_str} FROM {table_name}'
        print('>> ', query)

        cursor.execute(query)
        content: list = cursor.fetchall()  # type: ignore
        content = [list(row) for row in content]

        return TableContent(
            table_name=table_name, columns=columns, content=content)

    @staticmethod
    def _import_sql_file(cursor: MySQLCursor, filepath: str) -> None:
        """Initialize the schema and some sample data."""
        filepath = os.path.join(pathlib.Path().resolve(), filepath)
        with open(filepath, 'r', encoding='UTF-8') as fp:
            content = fp.read()
            statements = [s for s in content.split(';') if s.strip() != '']
            for s in statements:
                cursor.execute(s)

    @staticmethod
    def _drop_database(cnx: MySQLConnection, cursor: MySQLCursor) -> None:
        """Run the statement to remove a database."""
        cursor.execute(
            f'DROP DATABASE IF EXISTS `{DatabaseTest.DATABASE_NAME}`')
        cnx.commit()

    @staticmethod
    def _init_database(cnx: MySQLConnection, cursor: MySQLCursor) -> None:
        """Initialize a database and some sample content."""
        try:
            cursor.execute(f'CREATE DATABASE `{DatabaseTest.DATABASE_NAME}`')
            cursor.execute(f'USE `{DatabaseTest.DATABASE_NAME}`')
            cnx.commit()

            DatabaseTest._import_sql_file(
                cursor, DatabaseTest.SCHEMA_FILE)
            cnx.commit()

            DatabaseTest._import_sql_file(
                cursor, DatabaseTest.INIT_DATA_FILE)
            cnx.commit()
        except Exception as e:
            DatabaseTest._drop_database(cnx, cursor)
            cnx.commit()
            raise e
