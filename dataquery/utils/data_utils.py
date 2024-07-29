import datetime
import numpy as np
from sqlalchemy import types


def get_default_value(data_type):
    """
    Returns a default value for a given SQLAlchemy data type.
    """
    # Numeric types
    if issubclass(data_type, (types.Integer, types.BigInteger, np.integer)):
        value = 0
    elif issubclass(data_type, (types.Float, types.Numeric, np.floating)):
        value = 0.0

    # String types
    elif issubclass(data_type, (types.String, types.Text, types.CHAR, types.VARCHAR)):
        value = ""

    # Boolean type
    elif issubclass(data_type, types.Boolean):
        value = False

    # Date and Time types
    elif issubclass(data_type, (types.Date,)):
        value = datetime.date.min
    elif issubclass(data_type, (types.DateTime,)):
        value = datetime.datetime.min
    elif issubclass(data_type, (types.Time,)):
        value = datetime.time.min
    elif issubclass(data_type, (types.TIMESTAMP,)):
        value = datetime.datetime.min

    # Binary types
    elif issubclass(data_type, (types.LargeBinary, types.BINARY, types.VARBINARY)):
        value = b""
    return value
