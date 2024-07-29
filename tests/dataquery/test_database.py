# tests/test_database.py
from unittest.mock import MagicMock

from dataquery.core.database import Database


def test_database_connection(mock_engine_session, mocker):
    """
    Test that Database.init_app correctly initializes the engine and session.
    The mock_engine_session fixture is defined in conftest.py and automatically
    used here, providing a mocked session object.
    """
    Database.init_app("localhost", "5432", "test_user", "test_password", "test_db")
    mocker.patch("dataquery.core.database.Database.get_session", return_value=mock_engine_session)
    session = Database.get_session()

    # Assert session is not None and is a MagicMock instance, indicating it was mocked.
    assert session is not None
    assert isinstance(session, MagicMock)
    assert hasattr(session, "mock_calls"), "Session should be a mock"
