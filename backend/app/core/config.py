from pydantic_settings import BaseSettings
from pydantic import validator


class Settings(BaseSettings):
    # API Settings
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = True
    ENV: str = "development"

    # Security
    SECRET_KEY: str

    # CORS
    CORS_ORIGINS: list[str] = ["http://localhost:3000"]

    # Database
    DATABASE_URL: str
    POSTGRES_DB: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    
    # Database Pool Settings (optional - will use defaults if not set)
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_PRE_PING: bool = True
    DB_ECHO: bool = False
    DB_EXPIRE_ON_COMMIT: bool = False

    # Firebase
    FIREBASE_SERVICE_ACCOUNT_PATH: str

    # # Google Cloud Services
    # GOOGLE_APPLICATION_CREDENTIALS: str
    # GEMINI_API_KEY: str

    # pgAdmin Settings (for Docker Compose)
    PGADMIN_DEFAULT_EMAIL: str
    PGADMIN_DEFAULT_PASSWORD: str
    PGADMIN_CONFIG_SERVER_MODE: bool
    PGADMIN_CONFIG_MASTER_PASSWORD_REQUIRED: bool

    # Add these missing fields
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    TIMEZONE: str = "UTC"
    
    # Rate limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60  # seconds
    
    # File upload
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_FILE_TYPES: list[str] = ["image/jpeg", "image/png", "application/pdf"]
    
    # Logging
    LOG_LEVEL: str = "INFO"
    
    # Add validation
    @validator("CORS_ORIGINS", pre=True)
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings()