from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # App Settings
    APP_NAME: str = "Shopify Backend"
    DEBUG: bool = False
    
    # Shopify Settings
    SHOPIFY_API_KEY: str
    SHOPIFY_API_SECRET: str
    SHOPIFY_API_VERSION: str = "2024-04"
    SHOPIFY_SCOPES: str = "read_products,write_products,read_orders,write_orders"
    APP_URL: str # The URL where the app is hosted (for OAuth and webhooks)

    # Database Settings
    DATABASE_URL: str # asyncpg url: postgresql+asyncpg://user:pass@host/db
    
    # Redis Settings (for Celery)
    REDIS_URL: str = "redis://localhost:6379/0"

    # Firebase Settings
    FIREBASE_SERVICE_ACCOUNT_JSON: Optional[str] = None

    # Encryption Settings (for storing tokens)
    ENCRYPTION_KEY: str # 32-byte key for Fernet

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
