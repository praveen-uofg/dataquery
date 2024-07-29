# dataquery/dataquery/dataquery.py
import pandas as pd
from pandas import DataFrame

from dataquery.core.database import Database
from dataquery.core.retrieval import retrieve_data
from dataquery.core.table import get_table_names
from dataquery.core.column import get_columns_list, get_column_details
from dataquery.core.delete import delete_records
from dataquery.core.update import update_data
from dataquery.core.insert import insert_data
from dataquery.utils.logging_utils import setup_logging


class DataQuery:
    """
    A class for managing database operations in an abstracted and simplified manner.

    This class provides methods to interact with a database, including retrieving data,
    listing tables and columns, and performing CRUD operations, all through an easy-to-use
    interface that leverages SQLAlchemy and pandas for efficient data manipulation.

    Args:
        host (str): The database server host.
        port (int): The port number on which the database server is listening.
        username (str): The username used to authenticate with the database.
        password (str): The password used to authenticate with the database.
        database (str): The name of the database to connect to.
        debug (bool): If set to True, SQL queries will be logged for debugging purposes.
    """

    def __init__(self, host: str, port: int, username: str, password: str, database: str, debug: bool = False):
        """
        Initializes the database connection using provided credentials and optionally enables query logging.

        Args:
            host: The database server host.
            port: The port number on which the database server is listening.
            username: The username used to authenticate with the database.
            password: The password used to authenticate with the database.
            database: The name of the database to connect to.
            debug: If set to True, SQL queries will be logged for debugging purposes. Defaults to False.
        """
        Database.init_app(host, port, username, password, database, debug)
        setup_logging()

    @staticmethod
    def _get_connection():
        """
        Retrieves a context-managed database session.

        Returns:
            A context manager that yields a SQLAlchemy session.
        """
        return Database.session_scope()

    def list_table_names(self) -> list:
        """
        Retrieves a list of all table names in the database.

        Returns:
            A list of table names.
        """
        with self._get_connection() as session:
            return get_table_names(session)

    def list_columns(self, table_name: str) -> list:
        """
        Retrieves a list of all column names for a given table.

        Args:
            table_name: The name of the table to retrieve columns for.

        Returns:
            A list of column names for the specified table.
        """
        with self._get_connection() as session:
            return get_columns_list(session, table_name)

    def column_details(self, table_name: str, column_name: str) -> dict:
        """
        Retrieves details for a specific column in a given table.

        Args:
            table_name: The name of the table containing the column.
            column_name: The name of the column to retrieve details for.

        Returns:
            A dictionary containing details about the specified column.
        """
        with self._get_connection() as session:
            return get_column_details(session, table_name, column_name)

    def get_records(self, table_name: str, filter_criteria: dict = None) -> pd.DataFrame:
        """Retrieves data from a table and returns it as a pandas DataFrame.

        Args:
            table_name: The name of the table to retrieve data from.
            filter_criteria: Optional dictionary specifying filtering conditions.

        Returns:
            A pandas DataFrame containing the retrieved data.
        """
        with self._get_connection() as session:
            return retrieve_data(session, table_name, filter_criteria)

    def delete_records(self, table_name: str, filter_criteria: dict = None):
        """
        Deletes records from a table based on filter criteria.

        Args:
            table_name: The name of the table from which to delete records.
            filter_criteria: Optional dictionary specifying which records to delete.
        """
        with self._get_connection() as session:
            return delete_records(session, table_name, filter_criteria)

    def update_records(self, table_name: str, columns_to_match: list, data: DataFrame):
        """
        Updates records in a table based on matching columns and provided data.

        Args:
            table_name: The name of the table to update.
            columns_to_match: List of column names to match on for updating.
            data: A pandas DataFrame containing the data to update.
        """
        with self._get_connection() as session:
            return update_data(session, table_name, columns_to_match, data)

    def insert_records(self, table_name: str, data: DataFrame, unique_columns: list, return_rows: bool = False):
        """
        Inserts new rows of data into a table, ensuring no duplicates based on unique columns.

        Args:
            table_name: The name of the table to insert data into.
            data: A pandas DataFrame containing the data to insert.
            unique_columns: List of column names that uniquely identify a row in the table.
            return_rows (bool): If True, returns a DataFrame of the newly inserted rows. Defaults to False.

        """
        with self._get_connection() as session:
            return insert_data(session, table_name, data, unique_columns, return_rows)
