"""Environment configuration and SQLAlchemy session factory."""

import os
from pathlib import Path
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.engine import make_url
from sqlalchemy.orm import sessionmaker


def database_url():
    load_dotenv(Path(__file__).resolve().parent.parent / ".env")
    value = os.getenv("DATABASE_URL")
    if not value:
        raise RuntimeError(
            "Set DATABASE_URL in the environment or .env before starting BitRate"
        )
    return value


def make_engine(url):
    parsed = make_url(url)
    if parsed.get_backend_name() != "postgresql":
        raise ValueError("BitRate requires a PostgreSQL DATABASE_URL")
    return create_engine(
        parsed.set(drivername="postgresql+psycopg"), pool_pre_ping=True
    )


def session_factory(engine):
    return sessionmaker(bind=engine, expire_on_commit=False)
