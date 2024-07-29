import logging
from sqlalchemy import delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session
from dataquery.utils.db_utils import get_table, check_table_existence


logger = logging.getLogger(__name__)


def delete_records(session: Session, table_name: str, filter_criteria=None):
    try:
        # Reflect table from the database
        check_table_existence(session, table_name)
        table = get_table(session, table_name)

        # Construct a delete statement
        query = delete(table)

        if filter_criteria:
            for column, value in filter_criteria.items():
                if column not in table.c:
                    raise ValueError(f"Column '{column}' does not exist in table '{table_name}'.")
                query = query.where(table.c[column] == value)

        # Execute the query
        session.execute(query)
        session.commit()

        return "Records deleted successfully"

    except SQLAlchemyError as e:
        # Handle specific database errors (e.g., connection issues, query errors)
        logger.error("Database error occurred: %s", e)
        raise
    except ValueError as e:
        # Handle errors related to table or column existence
        logger.error("Value error: %s", e)
        raise
    except Exception as e:
        # Catch-all for any other unexpected errors
        logger.error("An unexpected error occurred: %s", e)
        raise
