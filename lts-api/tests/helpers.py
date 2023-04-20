from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
import os
import pathlib
from typing import Any, Tuple


class DatabaseTest:
    """
    Initialize a database to run the unit tests.

    Note that this class creates a new database on each class-level run and,
    once the tests have finished, it removes it.
    """

    DATABASE_NAME = os.environ.get('DB_DATABASE')
    INIT_DATA_FILE = 'data/init.sql'
    SAMPLE_DATA_FILE = 'data/sample.sql'
    SCHEMA_FILE = 'data/schema.sql'

    def setup_method(self, method: Any) -> None:  # noqa: U100
        """Set up."""
        DatabaseTest.reset_database()

    def teardown_method(self, method: Any) -> None:  # noqa: U100
        """Reset state of the database."""
        pass

    @staticmethod
    def reset_database() -> None:
        """Reset (remove and create) the database."""
        cnx, cursor = DatabaseTest._build_db_connection()
        DatabaseTest._drop_database(cnx, cursor)
        DatabaseTest._init_database(cnx, cursor)
        cursor.close()
        cnx.close()

    @staticmethod
    def _build_db_connection() -> Tuple[MySQLConnection, MySQLCursor]:
        """Build connection with the database."""
        cnx = MySQLConnection(
            host=os.environ.get('DB_HOST', None),
            port=os.environ.get('DB_PORT', None),
            user=os.environ.get('DB_USER', None),
            password=os.environ.get('DB_PASS', None))
        cnx.autocommit = False
        cursor = cnx.cursor()
        cursor.execute('SET NAMES "utf8";')
        return cnx, cursor

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
            DatabaseTest._import_sql_file(
                cursor, DatabaseTest.SAMPLE_DATA_FILE)
            cnx.commit()
        except Exception as e:
            DatabaseTest._drop_database(cnx, cursor)
            cnx.commit()
            raise e
