# dataquery/dataquery/core/retrieval.py
import logging
import pandas as pd
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dataquery.utils.db_utils import get_table, check_table_existence


logger = logging.getLogger(__name__)


def retrieve_data(session: Session, table_name: str, filter_criteria: dict = None):
    """
    Retrieves data from a table and returns it as a pandas DataFrame, with added error handling.

    Args:
        session (Session): An SQLAlchemy ORM session.
        table_name (str): The name of the table from which to retrieve data.
        filter_criteria (dict, optional): A dictionary of column-value pairs for filtering.

    Returns:
        DataFrame: A pandas DataFrame containing the retrieved data, or an empty DataFrame upon encountering an error.
    """
    try:
        # Reflect table from the database
        check_table_existence(session, table_name)
        _table = get_table(session, table_name)

        query = select(_table)

        if filter_criteria:
            for column, value in filter_criteria.items():
                if column not in _table.c:
                    raise ValueError(f"Column '{column}' does not exist in table '{table_name}'.")
                query = query.where(_table.c[column] == value)

        # Execute the query and fetch the results
        result_proxy = session.execute(query)

        # Convert to pandas DataFrame
        df = pd.DataFrame(result_proxy.fetchall(), columns=list(result_proxy.keys()))

    except SQLAlchemyError as e:
        # Handle specific database errors (e.g., connection issues, query errors)
        logger.error("Database error occurred: %s", e)
        df = pd.DataFrame()
    except ValueError as e:
        # Handle errors related to table or column existence
        logger.error("Value error: %s", e)
        df = pd.DataFrame()
    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.error("An unexpected error occurred: %s", e)
        df = pd.DataFrame()

    return df
