from typing import Any

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

# Base connect_args for the SQLAlchemy engine
connect_args: dict[str, Any] = {}

# Aiven MySQL requires SSL connections. If the CA path is provided via environment,
# we inject it into the connection arguments for PyMySQL.
if settings.DB_SSL_CA_PATH:
    connect_args["ssl"] = {"ca": settings.DB_SSL_CA_PATH}

engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    # Free-tier friendly connection pooling settings
    pool_size=5,
    max_overflow=10,
    pool_recycle=1800,  # Recycle connections after 30 minutes
    pool_pre_ping=True,  # Verify connection liveness before checking out
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
