# tests/conftest.py
import pytest
import json
from unittest.mock import MagicMock, patch
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

Base = declarative_base()


@pytest.fixture(scope="function")
def mock_engine_session():
    session_mock = MagicMock()
    scoped_session_mock = MagicMock(return_value=session_mock)

    with patch("dataquery.core.database.scoped_session", return_value=scoped_session_mock):
        yield session_mock


# Define a User model for testing
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String)
    gender = Column(String)


@pytest.fixture(scope="function")
def engine():
    """Creates a SQLite engine."""
    return create_engine("sqlite:///:memory:")


@pytest.fixture(scope="function")
def tables(engine):
    """Creates all tables for testing."""
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def session(engine, tables):
    """Creates a new database session for a test."""
    connection = engine.connect()
    transaction = connection.begin()
    _session = scoped_session(sessionmaker(bind=connection))
    _session.configure(bind=engine)

    yield _session

    _session.remove()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def populate_user_table(session):
    """Populates the user table with seed data from a JSON file."""
    with open("tests/seed_data.json", "r") as file:
        seed_data = json.load(file)
        for user_data in seed_data:
            user = User(**user_data)
            session.add(user)
        session.commit()
