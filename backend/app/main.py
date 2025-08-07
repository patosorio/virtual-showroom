import os
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

from .core.config import settings
from .core.database import Base, engine, init_db
from .core.firebase.auth import initialize_firebase
from .core.exceptions_handler import setup_exception_handlers

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import models to register them with SQLAlchemy (when they are created)
from .models.collection import Collection
from .models.product import (
    Product,
    ProductVariant,
    ProductImage,
    TechnicalSpecification,
    TechnicalDrawing,
    SizeChart
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting up Virtual Showroom API...")
    
    # Initialize Firebase Admin SDK
    try:
        initialize_firebase()
        logger.info("Firebase initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {str(e)}")
        raise
    
    # Initialize database
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {str(e)}")
        raise
    
    logger.info("Virtual Showroom API startup completed")
    
    yield
    
    # Shutdown
    logger.info("Shutting down Virtual Showroom API...")
    # Add any cleanup logic here if needed
    logger.info("Virtual Showroom API shutdown completed")


app = FastAPI(
    title="Virtual Showroom API",
    description="Backend API for the Virtual Showroom application",
    version="1.0.0",
    docs_url="/docs" if settings.ENV == "development" else None,
    redoc_url="/redoc" if settings.ENV == "development" else None,
    lifespan=lifespan
)

# Setup global exception handlers
setup_exception_handlers(app)
logger.info("Exception handlers configured")

# Configure CORS
cors_origins = settings.CORS_ORIGINS.copy() if settings.CORS_ORIGINS else []

dev_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000", 
    "https://localhost:3000"
]

for origin in dev_origins:
    if origin not in cors_origins:
        cors_origins.append(origin)

logger.info(f"CORS Origins configured: {cors_origins}")
logger.info(f"Environment: {settings.ENV}, Debug: {settings.DEBUG}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=[
        "Accept",
        "Accept-Language", 
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["Content-Length", "X-Total-Count"],
    max_age=600,  # Cache preflight requests for 10 minutes
)

# Add TrustedHost middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1", "*.yourdomain.com"])

# For production
if settings.ENV == "production":
    app.add_middleware(HTTPSRedirectMiddleware)

# Include API routes
from .core.api import router as api_router
app.include_router(api_router)


# Health check and utility endpoints
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "service": "Virtual Showroom API",
        "version": "1.0.0",
        "environment": os.getenv("ENV", "development")
    }


@app.get("/test-cors", tags=["Health"])
async def test_cors():
    """CORS test endpoint for development."""
    return {
        "message": "CORS test successful",
        "cors_origins": cors_origins,
        "environment": os.getenv("ENV", "development")
    }


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Welcome to Virtual Showroom API",
        "version": "1.0.0",
        "docs": "/docs" if os.getenv("ENV", "development") == "development" else "Documentation disabled in production",
        "health": "/health"
    }


# Add middleware for request logging in development
if os.getenv("ENV", "development") == "development":
    
    @app.middleware("http")
    async def log_requests(request, call_next):
        """Log all requests in development mode."""
        import time
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        # Process request
        response = await call_next(request)
        
        # Log response
        process_time = time.time() - start_time
        logger.info(
            f"Response: {response.status_code} - "
            f"Process time: {process_time:.4f}s"
        )
        
        return response


# Error handling verification endpoint (development only)
if os.getenv("ENV", "development") == "development":
    
    @app.get("/test-exceptions", tags=["Development"])
    async def test_exceptions(exception_type: str = "validation"):
        """Test different exception types (development only)."""
        from .core.exceptions import (
            ValidationError, NotFoundError, BadRequestError, 
            UnauthorizedError, InternalServerError
        )
        
        if exception_type == "validation":
            raise ValidationError(
                detail="Test validation error",
                context={"test": True}
            )
        elif exception_type == "notfound":
            raise NotFoundError(
                detail="Test not found error",
                context={"test": True}
            )
        elif exception_type == "badrequest":
            raise BadRequestError(
                detail="Test bad request error",
                context={"test": True}
            )
        elif exception_type == "unauthorized":
            raise UnauthorizedError(
                detail="Test unauthorized error",
                context={"test": True}
            )
        elif exception_type == "internal":
            raise InternalServerError(
                detail="Test internal server error",
                context={"test": True}
            )
        else:
            raise Exception("Test generic exception")
        
        return {"message": "This should not be reached"}