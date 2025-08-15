"""
Global exception handlers for the FastAPI application.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from .exceptions import AppBaseException

# FastAPI exception handlers
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: AppBaseException) -> JSONResponse:
    """Global exception handler for custom application exceptions."""
    logger.error(f"Application exception: {exc.detail}", extra={
        "error_code": exc.error_code,
        "context": exc.context,
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict()
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """Handle FastAPI HTTP exceptions."""
    logger.warning(f"HTTP exception: {exc.status_code} - {exc.detail}", extra={
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """Handle Pydantic validation errors."""
    logger.warning(f"Validation error: {exc.errors()}", extra={
        "path": request.url.path,
        "method": request.method
    })
    
    # Process validation errors to ensure they're JSON serializable
    errors = []
    for error in exc.errors():
        error_dict = {
            "type": error.get("type", "unknown_error"),
            "loc": error.get("loc", []),
            "msg": str(error.get("msg", "Unknown error")),
            "input": error.get("input")
        }
        # Handle ValueError in ctx
        ctx = error.get("ctx", {})
        if isinstance(ctx.get("error"), ValueError):
            error_dict["ctx"] = {"error": str(ctx["error"])}
        elif ctx:
            error_dict["ctx"] = ctx
        errors.append(error_dict)

    return JSONResponse(
        status_code=422,
        content={
            "error": True,
            "status_code": 422,
            "detail": "Validation failed",
            "error_code": "VALIDATION_ERROR",
            "errors": errors
        }
    )


async def starlette_http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    """Handle Starlette HTTP exceptions."""
    logger.error(f"Starlette HTTP exception: {exc.status_code} - {exc.detail}", extra={
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "status_code": exc.status_code,
            "detail": exc.detail or "Internal server error"
        }
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Generic exception handler for unexpected errors."""
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True, extra={
        "path": request.url.path,
        "method": request.method
    })
    
    return JSONResponse(
        status_code=500,
        content={
            "error": True,
            "status_code": 500,
            "detail": "An unexpected error occurred",
            "error_code": "INTERNAL_SERVER_ERROR"
        }
    )


def setup_exception_handlers(app):
    """Setup global exception handlers for the FastAPI application."""
    app.add_exception_handler(AppBaseException, global_exception_handler)
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, starlette_http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)