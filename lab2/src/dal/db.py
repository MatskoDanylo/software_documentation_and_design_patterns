from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    """Base SQLAlchemy declarative class."""


def create_sqlite_engine(db_path: str = "onboarding.db"):
    return create_engine(f"sqlite:///{db_path}", future=True)


def create_session_factory(engine):
    return sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)

