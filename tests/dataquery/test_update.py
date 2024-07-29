import pytest
import pandas as pd
from dataquery.core.update import update_data
from tests.conftest import User


@pytest.fixture
def test_data():
    return pd.DataFrame(
        {
            "id": [10090, 10020],
            "first_name": ["Joh", "Jane"],
            "last_name": ["Do", "Doe"],
            "email": ["joh@example.com", "jane@example.com"],
            "gender": ["Male", "Female"],
        }
    )


@pytest.fixture
def sample_update_data():
    return pd.DataFrame(
        {"id": [1, 2], "first_name": ["Deck", "July"], "email": ["john.updated@example.com", "jane.updated@example.com"]}
    )


def test_successful_update(engine, session, sample_update_data, populate_user_table):
    """
    Test that existing records are successfully updated.
    """

    message = update_data(session, "users", ["id"], sample_update_data)
    assert message == "Update successful."

    # Verify the data was updated
    user = session.query(User).filter_by(id=1).one()
    assert user.email == "john.updated@example.com", "Email was not updated correctly"


def test_update_nonexistent_table(session, sample_update_data, populate_user_table):
    """
    Test updating a table that doesn't exist.
    """
    with pytest.raises(ValueError) as excinfo:
        update_data(session, "nonexistent_table", ["id"], sample_update_data)
    assert "does not exist" in str(excinfo.value), "Nonexistent table error not handled correctly"


def test_update_nonexistent_column(session, sample_update_data, populate_user_table):
    """
    Test updating with a column that doesn't exist in the table.
    """
    with pytest.raises(ValueError) as excinfo:
        update_data(session, "users", ["nonexistent_column"], sample_update_data)
    assert "Columns do not exist" in str(excinfo.value), "Nonexistent column error not handled correctly"


def test_preprocessing_handles_nulls(session, populate_user_table):
    """
    Test that DataFrame preprocessing replaces null values with defaults.
    """
    data_with_nulls = pd.DataFrame(
        {
            "id": [1],
            "first_name": [None],  # Assuming 'first_name' allows nulls and has a default value
            "email": [None],  # email updated to None, should be replaced with default if defined
        }
    )
    update_data(session, "users", ["id"], data_with_nulls)

    user = session.query(User).filter_by(id=1).one()
    # Assuming get_default_value for String is '', replace '' with your actual default value
    assert user.first_name == "", "Null value was not replaced with default"
    assert user.email == "", "Email null value was not replaced with default"
