from fastapi import APIRouter

from app.api.routes import audits, findings, projects

router = APIRouter(prefix="/api/v1")
router.include_router(projects.router)
router.include_router(audits.router)
router.include_router(findings.router)
