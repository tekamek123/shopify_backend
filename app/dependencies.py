from typing import AsyncGenerator
from fastapi import Request, HTTPException, Header
from app.db.session import AsyncSessionLocal
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.auth_service import auth_service

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def validate_shopify_webhook(
    request: Request,
    x_shopify_hmac_sha256: str = Header(None)
):
    """
    Dependency to validate Shopify webhooks using HMAC.
    """
    if not x_shopify_hmac_sha256:
        raise HTTPException(status_code=401, detail="Missing HMAC header")

    body = await request.body()
    if not auth_service.verify_webhook_hmac(body, x_shopify_hmac_sha256):
        raise HTTPException(status_code=401, detail="HMAC verification failed")
    
    return body
