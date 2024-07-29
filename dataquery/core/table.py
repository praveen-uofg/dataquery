# dataquery/tables/table.py
from sqlalchemy import inspect


def get_table_names(session):
    """
    Retrieves all the table names in the database using an existing SQLAlchemy session.

    Args:
    - session: An SQLAlchemy session object.

    Returns:
    - List[str]: A list of table names in the database.
    """
    inspector = inspect(session.bind.engine)
    return inspector.get_table_names()
