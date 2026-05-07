import hmac
import hashlib
import httpx
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.config import settings
from app.models.db.merchant import Merchant

class AuthService:
    def __init__(self):
        # We'll initialize Fernet only if the key is available
        self.fernet = Fernet(settings.ENCRYPTION_KEY.encode())

    def verify_hmac(self, query_params: dict) -> bool:
        hmac_sig = query_params.get("hmac")
        if not hmac_sig:
            return False

        params = {k: v for k, v in query_params.items() if k != "hmac"}
        sorted_params = sorted(params.items())
        message = "&".join([f"{k}={v}" for k, v in sorted_params])

        hash_sig = hmac.new(
            settings.SHOPIFY_API_SECRET.encode(),
            message.encode(),
            hashlib.sha256
        ).hexdigest()

        return hmac.compare_digest(hash_sig, hmac_sig)

    async def exchange_code_for_token(self, shop: str, code: str) -> str:
        url = f"https://{shop}/admin/oauth/access_token"
        payload = {
            "client_id": settings.SHOPIFY_API_KEY,
            "client_secret": settings.SHOPIFY_API_SECRET,
            "code": code
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["access_token"]

    def encrypt_token(self, token: str) -> str:
        return self.fernet.encrypt(token.encode()).decode()

    async def save_merchant(self, db: AsyncSession, shop_domain: str, access_token: str):
        encrypted_token = self.encrypt_token(access_token)
        
        result = await db.execute(select(Merchant).where(Merchant.shop_domain == shop_domain))
        merchant = result.scalar_one_or_none()

        if merchant:
            merchant.access_token_encrypted = encrypted_token
            merchant.scopes = settings.SHOPIFY_SCOPES
        else:
            merchant = Merchant(
                shop_domain=shop_domain,
                access_token_encrypted=encrypted_token,
                scopes=settings.SHOPIFY_SCOPES
            )
            db.add(merchant)
        
        await db.commit()
        return merchant

auth_service = AuthService()
