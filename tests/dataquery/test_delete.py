import pytest
from sqlalchemy import select
from dataquery.core.delete import delete_records
from tests.conftest import User  # Adjust the import path as necessary

TEST_TABLE_NAME = "users"


def test_delete_records_table_exists(session, populate_user_table):
    test_record_id = 1

    # Perform delete operation
    msg = delete_records(session=session, table_name=TEST_TABLE_NAME, filter_criteria={"id": test_record_id})

    assert msg == "Records deleted successfully"

    # Fetch all records with the test_record_id to verify deletion
    result = session.execute(select(User).where(User.id == test_record_id)).fetchall()
    assert len(result) == 0, "Record was deleted"


def test_delete_all_records(session, populate_user_table):
    # Perform delete operation without filter criteria to delete all records
    delete_records(session=session, table_name=TEST_TABLE_NAME)

    # Check all records deleted
    all_users = session.execute(select(User)).fetchall()
    assert len(all_users) == 0, "Not all records were deleted"


def test_delete_records_table_does_not_exist(session):
    with pytest.raises(ValueError):
        delete_records(session=session, table_name="nonexistent_table")


def test_delete_records_column_does_not_exist(session, populate_user_table):
    with pytest.raises(ValueError):
        delete_records(session=session, table_name=TEST_TABLE_NAME, filter_criteria={"nonexistent_col": False})
