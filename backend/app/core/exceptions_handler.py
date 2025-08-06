"""
Global exception handlers for the FastAPI application.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse

from .exceptions import AppBaseException

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
    app.add_exception_handler(Exception, generic_exception_handler)