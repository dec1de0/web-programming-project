from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from app.database import make_engine, session_factory
from app.main import create_app
from app.models import Audit, Finding, Project


def test_restart_preserves_related_data(client, db_url):
    pid = client.post("/api/v1/projects", json={"name": "Persistent"}).json()["id"]
    aid = client.post(
        f"/api/v1/projects/{pid}/audits", json={"kind": "code", "source": 'eval("x")'}
    ).json()["id"]
    with TestClient(create_app(db_url)) as restarted:
        assert restarted.get(f"/api/v1/projects/{pid}").json()["name"] == "Persistent"
        assert restarted.get(f"/api/v1/audits/{aid}/findings").json()["total"] == 1
        assert (
            restarted.get(f"/api/v1/audits/{aid}/report").json()["initial_score"] == 80
        )


def test_constraints_rollback_and_cascade(client, db_url):
    pid = client.post("/api/v1/projects", json={"name": "Parent"}).json()["id"]
    client.post(
        f"/api/v1/projects/{pid}/audits", json={"kind": "code", "source": 'eval("x")'}
    )
    engine = make_engine(db_url)
    factory = session_factory(engine)
    with factory() as session:
        with pytest.raises(IntegrityError):
            with session.begin():
                session.add(Audit(project_id=uuid4(), kind="code", initial_score=100))
        with session.begin():
            assert session.scalar(select(func.count()).select_from(Audit)) == 1
        with pytest.raises(IntegrityError):
            with session.begin():
                finding = session.scalar(select(Finding))
                finding.status = "resolved"  # No note: database CHECK rejects this.
        with session.begin():
            assert session.scalar(select(Finding)).status == "open"
    assert client.delete(f"/api/v1/projects/{pid}").status_code == 204
    with factory() as session:
        for model in (Project, Audit, Finding):
            assert session.scalar(select(func.count()).select_from(model)) == 0
    engine.dispose()


def test_concurrent_unique_name(client):
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(
            pool.map(
                lambda _: client.post(
                    "/api/v1/projects", json={"name": "Same"}
                ).status_code,
                range(4),
            )
        )
    assert sorted(results) == [201, 409, 409, 409]
    assert (
        client.post("/api/v1/projects", json={"name": "After rollback"}).status_code
        == 201
    )


def test_migration_recreation(client, db_url):
    from pathlib import Path
    from alembic import command
    from alembic.config import Config
    from sqlalchemy import inspect

    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    config.attributes["database_url"] = db_url
    command.downgrade(config, "base")
    engine = make_engine(db_url)
    assert "projects" not in inspect(engine).get_table_names()
    command.upgrade(config, "head")
    assert {"projects", "audits", "findings"} <= set(inspect(engine).get_table_names())
    command.check(config)
    engine.dispose()
    assert (
        client.post("/api/v1/projects", json={"name": "After migration"}).status_code
        == 201
    )
