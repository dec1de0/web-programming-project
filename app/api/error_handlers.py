from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.errors import DomainError, ResourceConflict, ResourceNotFound
from app.schemas.common import ErrorDetail, ErrorResponse


def register_error_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def domain_error_handler(request: Request, exc: DomainError) -> JSONResponse:
        status = 422
        if isinstance(exc, ResourceNotFound):
            status = 404
        elif isinstance(exc, ResourceConflict):
            status = 409
        body = ErrorResponse(error=ErrorDetail(code=exc.code, message=exc.message))
        return JSONResponse(status_code=status, content=body.model_dump())
