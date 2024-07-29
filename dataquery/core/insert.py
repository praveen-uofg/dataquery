import logging
import pandas as pd
from sqlalchemy import update, and_, insert
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from dataquery.utils.db_utils import get_table, check_table_existence, check_columns_existence

logger = logging.getLogger(__name__)


def fetch_existing_unique_data(session, table, unique_columns):
    """
    Fetches existing rows from the table based on unique columns for comparison.
    """
    query = session.query(*[getattr(table.c, col) for col in unique_columns])
    return pd.read_sql(query.statement, session.bind)


def _identify_new_and_duplicate_entries(data, unique_columns, existing_unique_df):
    """
    Identifies new and duplicate entries based on unique columns and existing data.
    """

    # Reset index to ensure alignment, keeping the original index for reference
    data_reset_idx = data.reset_index(drop=False)

    unique_data = data[unique_columns].drop_duplicates().reset_index(drop=False)

    # Reset existing_unique_df index without dropping, to keep original indexing
    existing_unique_df_reset_idx = existing_unique_df.reset_index(drop=False)

    # Merge with an indicator to distinguish new from existing entries
    merged_df = unique_data.merge(existing_unique_df_reset_idx, on=unique_columns, how="outer", indicator=True)

    # Determine new entries (those only in 'left' DataFrame)
    new_entries = merged_df.loc[merged_df["_merge"] == "left_only"]

    # Using the original 'index' column to select rows from data
    new_entries_final = data_reset_idx.loc[data_reset_idx["index"].isin(new_entries["index_x"])].drop(columns=["index"])

    # Determine duplicate entries (those found in both DataFrames)
    duplicate_entries = merged_df.loc[merged_df["_merge"] == "both"]

    # Using the original 'index' column to select rows from data
    duplicate_entries_final = data_reset_idx.loc[data_reset_idx["index"].isin(duplicate_entries["index_x"])].drop(
        columns=["index"]
    )

    return new_entries_final, duplicate_entries_final


def insert_new_entries(session, table_name, new_entries):
    """
    Inserts new entries into the table.
    """
    if not new_entries.empty:
        logger.info("Inserting new entries. Rows: %s", new_entries.shape[0])
        new_entries.to_sql(table_name, con=session.bind, if_exists="append", index=False)


def update_duplicate_entries(session, table, duplicate_entries, unique_columns):
    """
    Updates duplicate entries in the table.
    """
    logger.info("Updating duplicate records. Rows: %s", duplicate_entries.shape[0])
    for _, row in duplicate_entries.iterrows():
        update_stmt = (
            update(table).where(and_(*[table.c[col] == row[col] for col in unique_columns])).values(row.to_dict())
        )
        session.execute(update_stmt)


def _insert_entries_return_rows(session, table, new_entries):
    """
    Inserts new entries into the table and returns the newly inserted rows.

    Args:
        session (Session): An SQLAlchemy ORM session.
        table (Table): The SQLAlchemy table object to insert data into.
        new_entries (DataFrame): The pandas DataFrame containing new entries to insert.

    Returns:
        DataFrame: A DataFrame containing the newly inserted rows.
    """
    # Convert the DataFrame to a list of dictionaries for bulk insert
    new_entries_dicts = new_entries.to_dict(orient="records")

    if new_entries_dicts:
        # Use the insert expression with a returning clause
        stmt = insert(table).returning(*table.c).values(new_entries_dicts)
        result = session.execute(stmt)
        # Fetch the results of the returning clause
        inserted_rows = result.fetchall()
        # Convert the results back to a DataFrame
        inserted_df = pd.DataFrame(inserted_rows)
        return inserted_df
    else:
        # Return an empty DataFrame if there were no new entries
        return pd.DataFrame(columns=new_entries.columns)


def insert_data(
    session: Session, table_name: str, data: pd.DataFrame, unique_columns: list, return_rows: bool = False
) -> str | pd.DataFrame:
    """
    Add new rows of data to an existing table or update partially duplicate rows.

        Args:
            session (Session): An SQLAlchemy ORM session.
            table_name (str): The name of the table.
            data (pd.DataFrame): Data to be inserted or updated.
            unique_columns (list): A list of column names that uniquely identify a row.
            return_rows (bool): If True, returns a DataFrame of the newly inserted rows. Defaults to False.

        Returns:
            str | pd.DataFrame: A success/failure message or a DataFrame of newly inserted rows, depending on the value of `return_rows`.
    """

    # Check if the DataFrame is empty
    if data.empty:
        logger.info("No data to insert or update.")
        return "No data to insert or update."

    try:
        check_table_existence(session, table_name)
        check_columns_existence(session, table_name, unique_columns)
        table = get_table(session, table_name)

        data = data.drop_duplicates(subset=unique_columns, keep="first")  # Drop complete duplicates

        existing_unique_df = fetch_existing_unique_data(session, table, unique_columns)

        # new_entries, duplicate_entries = identify_new_and_duplicate_entries(data, unique_columns, existing_unique_df)
        new_entries, duplicate_entries = _identify_new_and_duplicate_entries(data, unique_columns, existing_unique_df)

        if return_rows:
            result = _insert_entries_return_rows(session, table, new_entries)
        else:
            insert_new_entries(session, table_name, new_entries)
            result = "Data added or updated successfully."
        update_duplicate_entries(session, table, duplicate_entries, unique_columns)

        session.commit()
        return result
    except SQLAlchemyError as e:
        session.rollback()
        logger.error("Database error occurred: %s", e)
        raise
    except ValueError as e:
        logger.error("Error: %s", e)
        raise
    except Exception as e:
        session.rollback()  # Ensuring session rollback on generic errors
        logger.error("An unexpected error occurred: %s", e)
        raise
