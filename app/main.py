from contextlib import asynccontextmanager
from fastapi import FastAPI
from app.api.error_handlers import register_error_handlers
from app.api.router import router
from app.api.routes.health import router as health_router
from app.database import database_url, make_engine, session_factory


def create_app(url: str | None = None) -> FastAPI:
    @asynccontextmanager
    async def lifespan(application):
        engine = make_engine(url or database_url())
        application.state.session_factory = session_factory(engine)
        try:
            yield
        finally:
            engine.dispose()

    application = FastAPI(
        title="BitRate API",
        version="0.2.0",
        lifespan=lifespan,
        description="Independent code/security and frontend design assessments.",
    )
    register_error_handlers(application)
    application.include_router(health_router)
    application.include_router(router)
    return application


app = create_app()
