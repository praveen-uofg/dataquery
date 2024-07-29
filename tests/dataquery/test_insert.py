import pytest
import pandas as pd
from dataquery.core.insert import insert_data
from tests.conftest import User

SUCCESS_MESSAGE = "Data added or updated successfully."


@pytest.fixture
def test_data():
    return pd.DataFrame(
        {
            "id": [10010, 10020],
            "first_name": ["John", "Jane"],
            "last_name": ["Doe", "Doe"],
            "email": ["john@example.com", "jane@example.com"],
            "gender": ["Male", "Female"],
        }
    )


@pytest.fixture
def sample_duplicate_data():
    return pd.DataFrame(
        {
            "id": [1, 20000, 1],  # Note the duplicate ID
            "first_name": ["John", "Jane", "John"],
            "last_name": ["Doe", "Doe", "Smith"],  # Different last name for the duplicate
            "email": ["john@example.com", "jane@example.com", "johnsmith@example.com"],
            "gender": ["Male", "Female", "Male"],
        }
    )


def test_insert_new_entries(session, test_data):
    """
    Test inserting new records into the database.
    """
    message = insert_data(session, "users", test_data, ["id"])
    assert message == SUCCESS_MESSAGE

    # Verify data was inserted
    inserted_records = session.query(User).count()
    assert inserted_records == 2


def test_update_existing_entries(session, test_data):
    """
    Test updating existing records.
    """
    insert_data(session, "users", test_data, ["id"])
    # Modify test_data to simulate an update
    test_data.loc[0, "email"] = "updated_john@example.com"

    message = insert_data(session, "users", test_data.head(1), ["id"])  # Update only the first row
    assert message == SUCCESS_MESSAGE

    updated_user = session.query(User).filter_by(id=10010).one()
    assert updated_user.email == "updated_john@example.com"


def test_nonexistent_table(session, test_data, populate_user_table):
    """
    Test handling attempts to insert data into a nonexistent table.
    """
    with pytest.raises(ValueError) as excinfo:
        insert_data(session, "nonexistent_table", test_data, ["id"])
    assert "does not exist" in str(excinfo.value)


def test_complete_duplicates_removed(session, sample_duplicate_data):
    # Assuming a fixture `populate_user_table` to add initial data
    # Adjust `insert_data` call as necessary, based on its location and parameters
    insert_data(session, "users", sample_duplicate_data.drop_duplicates(), ["id"])
    assert session.query(User).count() == 2  # Expect 2 because of duplicate removal


def test_partial_duplicates_update(session, sample_duplicate_data, populate_user_table):
    insert_data(session, "users", sample_duplicate_data, ["id"])
    updated_user = session.query(User).filter_by(id=1).one()
    assert updated_user.last_name == "Doe", "Partial duplicate was not updated correctly"


def test_nonexistent_column_in_unique_columns(session, sample_duplicate_data, populate_user_table):
    with pytest.raises(ValueError):
        insert_data(session, "users", sample_duplicate_data, ["nonexistent_column"])


def test_insert_with_empty_dataframe(session, populate_user_table):
    empty_df = pd.DataFrame()
    message = insert_data(session, "users", empty_df, ["id"])
    assert message == "No data to insert or update.", "Function did not handle empty DataFrame gracefully"


def test_large_volume_of_rows(session, populate_user_table):
    large_data = pd.DataFrame(
        {
            "id": range(1000, 2000),
            "first_name": ["Name"] * 1000,
            "last_name": ["Surname"] * 1000,
            "email": [f"user{i}@example.com" for i in range(1000, 2000)],
            "gender": ["Other"] * 1000,
        }
    )
    message = insert_data(session, "users", large_data, ["id"])
    assert message == SUCCESS_MESSAGE, "Failed to handle a large volume of rows"
