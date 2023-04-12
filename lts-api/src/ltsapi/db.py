from logging import Logger
from mysql.connector.connection import MySQLConnection
from mysql.connector.cursor import MySQLCursorDict
from typing import Optional


class DBContext:
    """
    Wrapper of database connections.

    Sample use:
    > from ltsapi.db import DBContext
    > db = DBContext(...)
    > with db as cnx:
    >     cnx.execute('SELECT * FROM employees')
    """

    def __init__(
            self,
            host: Optional[str],
            port: Optional[str],
            user: Optional[str],
            password: Optional[str],
            database: Optional[str],
            logger: Logger) -> None:
        """Construct."""
        self._host = host
        self._port = port
        self._user = user
        self._password = password
        self._database = database
        self._logger = logger
        self._cnx: Optional[MySQLConnection] = None
        self._cursor: Optional[MySQLCursorDict] = None

    def __enter__(self) -> MySQLCursorDict:
        """Open connection with database."""
        self._logger.info(
            f'Open connection with {self._host} (port: {self._port}, '
            f'database: {self._database}, username: {self._user}).')
        self._cnx = MySQLConnection(
            host=self._host,
            port=self._port,
            user=self._user,
            password=self._password,
            database=self._database)
        self._cnx.set_charset_collation('utf8mb4', 'utf8mb4_unicode_ci')
        c: MySQLCursorDict = self._cnx.cursor(dictionary=True)  # type: ignore
        c.execute('SET NAMES utf8;')
        self._cursor = c
        return c

    def __exit__(self, *args) -> None:  # noqa: ANN002, U100
        """Close connection with database."""
        self._logger.info(f'Close connection with {self._host}.')
        self._cursor.close()  # type: ignore
        self._cnx.close()  # type: ignore

    def get_connection(self) -> MySQLConnection:
        """Return MySQL connection instance."""
        if self._cnx is None:
            raise Exception('Connection not initialized yet.')
        return self._cnx

    def get_cursor(self) -> MySQLCursorDict:
        """Return MySQL cursor instance."""
        if self._cursor is None:
            raise Exception('Connection not initialized yet.')
        return self._cursor

    def commit(self) -> None:
        """Do commit."""
        if self._cnx is None:
            raise Exception('Connection not initialized yet.')
        self._cnx.commit()

    def rollback(self) -> None:
        """Do rollback."""
        if self._cnx is None:
            raise Exception('Connection not initialized yet.')
        self._cnx.rollback()

    def start_transaction(self) -> None:
        """Start a transaction."""
        if self._cnx is None:
            raise Exception('Connection not initialized yet.')
        self._cnx.start_transaction()
