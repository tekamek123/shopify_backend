from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class Settings(BaseSettings):
    # Shopify Settings
    SHOPIFY_API_KEY: str
    SHOPIFY_API_SECRET: str
    SHOPIFY_API_VERSION: str = "2024-04"
    SHOPIFY_SCOPES: str = "read_products,write_products,read_orders,write_orders"
    APP_URL: str # The URL where the app is hosted (e.g. ngrok URL)

    # Database Settings
    DATABASE_URL: str
    
    # Redis Settings
    REDIS_URL: str
    
    # Security Settings
    JWT_SECRET: str
    ENCRYPTION_KEY: str # 32-byte key for Fernet
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # App Settings
    APP_NAME: str = "Shopify Backend"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
