# dataquery/columns/column.py

from sqlalchemy import inspect


def get_columns_list(session, table_name):
    """
    Retrieves a list of column names for a given table.

    Args:
    - session: An SQLAlchemy session object.
    - table_name (str): The name of the table to retrieve columns for.

    Returns:
    - List[str]: A list of column names for the specified table.
    """
    inspector = inspect(session.bind.engine)
    return [column['name'] for column in inspector.get_columns(table_name)]


def get_column_details(session, table_name, column_name):
    """
    Retrieves all details for a specific column in a given table.

    Args:
    - session: An SQLAlchemy session object.
    - table_name (str): The name of the table.
    - column_name (str): The name of the column to retrieve details for.

    Returns:
    - Dict: A dictionary of column details.
    """
    inspector = inspect(session.bind.engine)
    columns = inspector.get_columns(table_name)
    for column in columns:
        if column['name'] == column_name:
            return column
    return None
