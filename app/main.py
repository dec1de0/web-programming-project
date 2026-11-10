from fastapi import FastAPI

from app.api.error_handlers import register_error_handlers
from app.api.router import router
from app.api.routes.health import router as health_router


def create_app() -> FastAPI:
    application = FastAPI(
        title="BitRate API",
        version="0.1.0",
        description="Independent code/security and frontend design assessments.",
    )
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(router)
    return application


app = create_app()
