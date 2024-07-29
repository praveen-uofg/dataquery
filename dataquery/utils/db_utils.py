from sqlalchemy import MetaData, inspect


def get_table(session, table_name):
    metadata_obj = MetaData()
    metadata_obj.reflect(bind=session.bind.engine)
    table = metadata_obj.tables.get(table_name)
    if table is None:
        raise ValueError(f"Table '{table_name}' does not exist.")
    return table


def check_table_existence(session, table_name):
    """
    Checks if the specified table exists in the database.
    Args:
        session (Session): An SQLAlchemy ORM session.
        table_name (str): The name of the table to check existence for.
    Raises:
        ValueError: If the table does not exist in the database.
    """
    inspector = inspect(session.bind.engine)
    if table_name not in inspector.get_table_names():
        raise ValueError("Table does not exist in the database.")


def check_columns_existence(session, table_name, columns_to_match):
    """
    Verifies the existence of specified columns in a table.
    Args:
        session (Session): An SQLAlchemy ORM session.
        table_name (str): The name of the table to check columns in.
        columns_to_match (list): List of column names to verify existence for.
    Raises:
        ValueError: If any of the specified columns do not exist in the table.
    """
    inspector = inspect(session.bind.engine)
    table_columns = [column["name"] for column in inspector.get_columns(table_name)]
    if not all(column in table_columns for column in columns_to_match):
        missing_columns = [column for column in columns_to_match if column not in table_columns]
        raise ValueError(f"Columns do not exist in table '{table_name}': {missing_columns}")
