# tests/test_column.py
from unittest.mock import MagicMock
import pytest
from dataquery.core.column import get_columns_list, get_column_details


@pytest.fixture
def setup_mock_engine(mocker):
    # Mock the inspect function and its get_columns method
    mock_inspect = mocker.patch("dataquery.core.column.inspect")
    mock_inspect.return_value.get_columns.return_value = [
        {"name": "column1", "type": "VARCHAR", "nullable": False},
        {"name": "column2", "type": "INTEGER", "nullable": True},
    ]


def test_get_columns_list(setup_mock_engine, mock_engine_session):
    session = MagicMock()
    columns = get_columns_list(session, "your_table_name")
    assert columns == ["column1", "column2"]


def test_get_column_details(setup_mock_engine, mock_engine_session):
    session = MagicMock()
    column_details = get_column_details(session, "your_table_name", "column1")
    assert column_details == {"name": "column1", "type": "VARCHAR", "nullable": False}
