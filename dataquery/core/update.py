# dataquery/dataquery/core/update.py
import logging
from pandas import DataFrame
from sqlalchemy import update, inspect
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dataquery.utils.data_utils import get_default_value

from dataquery.utils.db_utils import get_table, check_table_existence, check_columns_existence

# from collections import defaultdict
# from sqlalchemy import and_

logger = logging.getLogger(__name__)


def update_data(session: Session, table_name: str, columns_to_match: list, data: DataFrame) -> str:
    """
    Updates specific rows in a table based on matching columns and provided data, ensuring data integrity.
    Args:
        session (Session): An SQLAlchemy ORM session.
        table_name (str): The name of the table to update data in.
        columns_to_match (list): List of column names to match on to update.
        data (DataFrame): Pandas DataFrame containing the data to be updated.
    Returns:
        str: Success or failure notification.
    """
    try:
        check_table_existence(session, table_name)
        check_columns_existence(session, table_name, columns_to_match)

        table = get_table(session, table_name)

        # Preprocess DataFrame before the update loop
        data = preprocess_dataframe(data, table, session)

        for _, row in data.iterrows():
            __update_data_row(session, table, columns_to_match, row)

        session.commit()
        return "Update successful."
    except SQLAlchemyError as e:
        logger.error("Database error occurred during update: %s", e)
        session.rollback()
        # return "Update failed due to database error."
        raise
    except ValueError as e:
        logger.error("Value error occurred: %s", e)
        # return "Update failed due to value error."
        raise
    except Exception as e:
        logger.error("An unexpected error occurred: %s", e)
        session.rollback()
        raise
        # return "Update failed due to an unexpected error."


def preprocess_dataframe(data, table, session):
    """
    Preprocesses the DataFrame to replace NaN values and empty strings with default values based on column data types.

    Args:
        data (DataFrame): The pandas DataFrame containing the data to be updated.
        table: The SQLAlchemy table object.
        session (Session): The SQLAlchemy session.

    Returns:
        DataFrame: The preprocessed DataFrame.
    """
    inspector = inspect(session.bind.engine)
    column_info = inspector.get_columns(table.name)
    column_defaults = {}

    for column in column_info:
        column_name = column["name"]
        column_type = column["type"].__class__
        default_value = get_default_value(column_type)
        column_defaults[column_name] = default_value

    # Replace NaN and empty strings for columns in the DataFrame that are also in the table
    for column in data.columns.intersection(column_defaults.keys()):
        data[column] = data[column].fillna(column_defaults[column])
        if issubclass(column_defaults[column].__class__, str):
            data[column] = data[column].replace({"": column_defaults[column]})

    return data


def __update_data_row(session, table, columns_to_match, row):
    """
    Updates a single row in the table based on matching columns with the provided data.
    Args:
        session (Session): An SQLAlchemy ORM session.
        table: The table object to update.
        columns_to_match (list): List of column names to match for updating.
        row: The row data to update in the table.
    """
    match_condition = [table.c[column] == row[column] for column in columns_to_match]

    stmt = update(table).where(*match_condition).values(row.to_dict())
    session.execute(stmt)


# In case we need bulk update in future

# def perform_grouped_bulk_updates(session, table, update_groups):
#     """
#     Perform bulk updates for grouped data.
#     Args:
#         session (Session): SQLAlchemy session.
#         table: SQLAlchemy table object.
#         update_groups (dict): A dictionary where keys are tuples representing the
#                               match conditions (columns_to_match values), and values are
#                               lists of dictionaries with the data to update.
#     """
#     for match_values, updates in update_groups.items():
#         # Assuming match_values is a tuple of values corresponding to columns_to_match
#         # and updates is a list of dictionaries with the new data for these rows
#         for update_data in updates:
#             stmt = (
#                 update(table)
#                 .where(and_(*[table.c[col] == val for col, val in zip(columns_to_match, match_values)]))
#                 .values(**update_data)
#             )
#             session.execute(stmt)
#     session.commit()
#
# def update_data(session: Session, table_name: str, columns_to_match: list, data: DataFrame):
#     # Similar setup as before, up to including table reflection
#
#     # Group updates by unique combinations of columns_to_match
#     update_groups = defaultdict(list)
#     for _, row in data.iterrows():
#         match_values = tuple(row[col] for col in columns_to_match)
#         update_groups[match_values].append(row.to_dict())
#
#     # Perform grouped bulk updates
#     perform_grouped_bulk_updates(session, table, update_groups)
#
#     # Error handling remains similar to before
