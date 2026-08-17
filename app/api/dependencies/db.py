from collections.abc import Generator

from sqlalchemy.orm import Session

from app.core.database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that provides a SQLAlchemy Session per request.
    Ensures that the session is closed cleanly after the request finishes.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
