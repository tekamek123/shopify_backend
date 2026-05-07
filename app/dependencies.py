from typing import AsyncGenerator
from fastapi import Request, HTTPException, Header, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import AsyncSessionLocal
from app.services.auth_service import auth_service
from app.services.token_service import token_service
from app.models.db.merchant import Merchant

security = HTTPBearer()

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

async def get_current_merchant(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Merchant:
    """
    Dependency to get the currently authenticated merchant from JWT.
    """
    token = credentials.credentials
    payload = token_service.decode_token(token)
    
    if not payload or payload.get("type") != "access":
        raise HTTPException(status_code=401, detail="Invalid or expired access token")
    
    merchant_id = payload.get("sub")
    if not merchant_id:
        raise HTTPException(status_code=401, detail="Invalid token payload")

    result = await db.execute(select(Merchant).where(Merchant.id == int(merchant_id)))
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found")
        
    return merchant
