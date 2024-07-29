# dataquery/dataquery/database.py
from contextlib import contextmanager
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import declarative_base

db_session = scoped_session(sessionmaker(autocommit=False, autoflush=False))
Base = declarative_base()


class Database:
    engine: Engine = None  # Class-level attribute for the engine

    @classmethod
    def init_app(cls, host: str, port: int, username: str, password: str, database: str, debug: bool = False) -> None:
        """
        Initializes the database application with the given configuration.

        Args:
            host: Database host address.
            port: Database port number.
            username: Database user name.
            password: Database password.
            database: Database name.
            debug: If True, SQL statements will be echoed.
        """
        database_url = f"postgresql://{username}:{password}@{host}:{port}/{database}"
        cls.engine = create_engine(database_url, echo=debug)
        db_session.configure(bind=cls.engine)
        # Optional: Base.metadata.create_all(bind=cls.engine)

    @staticmethod
    @contextmanager
    def session_scope():
        """
        Provide a transactional scope around a series of operations.
        """
        session = db_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    @classmethod
    def get_session(cls) -> scoped_session:
        """
        Gets the current scoped session.

        Returns:
            The scoped session object.
        """
        return db_session

    @classmethod
    def shutdown(cls) -> None:
        """
        Removes the current session.
        """
        db_session.remove()
