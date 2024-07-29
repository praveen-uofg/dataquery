# tests/test_table.py
from unittest.mock import MagicMock
from dataquery.core.table import get_table_names


def test_get_table_names(mock_engine_session, mocker):
    # Mock the inspect function to return a mock inspector with a mocked get_table_names method
    mock_inspector = MagicMock()
    mock_inspector.get_table_names.return_value = ['table1', 'table2']
    mocker.patch('dataquery.core.table.inspect', return_value=mock_inspector)

    # Assuming get_table_names correctly uses SQLAlchemy's inspect
    tables = get_table_names(mock_engine_session)
    assert tables == ['table1', 'table2']
