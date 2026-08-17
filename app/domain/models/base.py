from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy 2.x declarative models.
    All ORM models must inherit from this class to be detected by Alembic.
    """
    pass
