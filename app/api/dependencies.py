from fastapi import Request
from sqlalchemy.exc import IntegrityError
from app.errors import ResourceConflict


def get_session(request: Request):
    """One transaction per request; commit before response, rollback on error, always close."""
    try:
        with request.app.state.session_factory() as session:
            with session.begin():
                yield session
    except IntegrityError as exc:
        constraint = getattr(getattr(exc.orig, "diag", None), "constraint_name", "")
        if constraint == "projects_name_key_key":
            raise ResourceConflict(
                "Project name already exists", code="project_name_taken"
            ) from exc
        raise ResourceConflict(
            "Operation conflicts with database constraints or related records",
            code="integrity_conflict",
        ) from exc
