from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursor
import os
import pathlib
from typing import Tuple


class DatabaseTestInit:
    """
    Initialize a database to run the unit tests.

    Note that this class creates a new database on each class-level run and,
    once the tests have finished, it removes it.
    """

    DATABASE_NAME = os.environ.get('DB_DATABASE')
    SAMPLE_DATA_FILE = os.path.join('data', 'sample.sql')
    SCHEMA_FILE = os.path.join('data', 'schema.sql')

    def setup_method(self) -> None:
        """Set up a database."""
        # Connect to MySQL and create a database
        cnx, cursor = self._build_db_connection()
        self._drop_database(cursor)
        self._create_database(cursor)
        cnx.commit()

        # Create schema and import sample data
        try:
            self._import_sql_file(
                cursor, self.SCHEMA_FILE)
            cnx.commit()

            self._import_sql_file(
                cursor, self.SAMPLE_DATA_FILE)
            cnx.commit()
        except Exception as e:
            self._drop_database(cursor)
            cnx.commit()
            raise e

        # Close connection
        cursor.close()
        cnx.close()

    def teardown_method(self) -> None:
        """Remove a database."""
        cnx, cursor = self._build_db_connection()
        self._drop_database(cursor)
        cursor.close()
        cnx.close()

    def _build_db_connection(self) -> Tuple[MySQLConnection, MySQLCursor]:
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

    def _create_database(self, cursor: MySQLCursor) -> None:
        """Create a database and select it."""
        cursor.execute(f'CREATE DATABASE `{self.DATABASE_NAME}`')
        cursor.execute(f'USE `{self.DATABASE_NAME}`')

    def _import_sql_file(self, cursor: MySQLCursor, filepath: str) -> None:
        """Initialize the schema and some sample data."""
        filepath = os.path.join(pathlib.Path().resolve(), filepath)
        with open(filepath, 'r', encoding='UTF-8') as fp:
            content = fp.read()
            statements = [s for s in content.split(';') if s.strip() != '']
            for s in statements:
                cursor.execute(s)

    def _drop_database(self, cursor: MySQLCursor) -> None:
        """Run the statement to remove a database."""
        cursor.execute(f'DROP DATABASE IF EXISTS `{self.DATABASE_NAME}`')
