"""Integration tests use real PostgreSQL, migrated with Alembic."""

import os
from pathlib import Path
import pytest
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv
from sqlalchemy import text
from sqlalchemy.engine import make_url
from fastapi.testclient import TestClient
from app.database import make_engine
from app.main import create_app


@pytest.fixture(scope="session")
def db_url():
    load_dotenv(Path(__file__).resolve().parents[1] / ".env")
    url = os.getenv("TEST_DATABASE_URL")
    if not url:
        pytest.skip(
            "Set TEST_DATABASE_URL to a separate PostgreSQL database ending in _test"
        )
    if not (make_url(url).database or "").endswith("_test"):
        pytest.fail("Test database name must end in _test; tests erase its data")
    application_url = os.getenv("DATABASE_URL")
    if application_url and make_url(url).database == make_url(application_url).database:
        pytest.fail("TEST_DATABASE_URL must use a different database from DATABASE_URL")
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["database_url"] = url
    command.upgrade(config, "head")
    return url


@pytest.fixture
def client(db_url):
    engine = make_engine(db_url)
    with engine.begin() as connection:
        connection.execute(text("TRUNCATE findings, audits, projects CASCADE"))
    engine.dispose()
    with TestClient(create_app(db_url)) as client:
        yield client
