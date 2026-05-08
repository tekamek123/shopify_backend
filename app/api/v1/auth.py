import uuid
import urllib.parse
from fastapi import APIRouter, Query, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.config import settings
from app.dependencies import get_db
from app.services.auth_service import auth_service
from app.services.webhook_service import webhook_service
from app.services.token_service import token_service
from app.models.db.merchant import Merchant
from app.models.schemas.auth import TokenRequest, TokenResponse, RefreshRequest

router = APIRouter()

@router.get("/install")
async def install(response: Response, shop: str = Query(...)):
    """
    Step 1: Validate shop and redirect to Shopify OAuth with state nonce.
    """
    if not shop.endswith(".myshopify.com"):
        raise HTTPException(status_code=400, detail="Invalid shop domain")

    # Generate a unique state nonce and store it in a secure cookie
    state = str(uuid.uuid4())
    
    redirect_uri = f"{settings.APP_URL}/api/v1/auth/callback"
    params = {
        "client_id": settings.SHOPIFY_API_KEY,
        "scope": settings.SHOPIFY_SCOPES,
        "redirect_uri": redirect_uri,
        "state": state
    }
    
    auth_url = f"https://{shop}/admin/oauth/authorize?{urllib.parse.urlencode(params)}"
    
    # Set state in a secure cookie to verify in callback
    response = RedirectResponse(url=auth_url)
    response.set_cookie(
        key="shopify_state",
        value=state,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=600 # 10 minutes
    )
    return response

@router.get("/callback")
async def callback(
    request: Request,
    shop: str = Query(...),
    code: str = Query(...),
    state: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Handle callback, verify HMAC, exchange code for token, and register webhooks.
    """
    # 1. Verify state nonce from cookie
    cookie_state = request.cookies.get("shopify_state")
    if not cookie_state or cookie_state != state:
        raise HTTPException(status_code=403, detail="State nonce verification failed")

    # 2. Verify HMAC signature
    query_params = dict(request.query_params)
    if not auth_service.verify_hmac(query_params):
        raise HTTPException(status_code=401, detail="HMAC verification failed")

    # 3. Exchange temporary code for permanent access token
    try:
        access_token = await auth_service.exchange_code_for_token(shop, code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {str(e)}")

    # 4. Encrypt token and upsert Merchant record
    await auth_service.save_merchant(db, shop, access_token)

    # 4. Register mandatory webhooks
    await webhook_service.register_webhooks(shop, access_token)

    # 5. Redirect to Shopify Admin
    app_handle = settings.APP_NAME.replace(' ', '-').lower()
    return RedirectResponse(url=f"https://{shop}/admin/apps/{app_handle}")

@router.post("/token", response_model=TokenResponse)
async def get_token(
    data: TokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    Issue access and refresh tokens for the Flutter app.
    """
    result = await db.execute(select(Merchant).where(Merchant.shop_domain == data.shop))
    merchant = result.scalar_one_or_none()
    
    if not merchant:
        raise HTTPException(status_code=404, detail="Merchant not found.")

    token_data = {"sub": str(merchant.id), "shop": merchant.shop_domain}
    access_token = token_service.create_access_token(token_data)
    refresh_token = token_service.create_refresh_token(token_data)
    
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    data: RefreshRequest,
):
    """
    Validate refresh token and issue a new access token.
    """
    payload = token_service.decode_token(data.refresh_token)
    
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    token_data = {"sub": payload.get("sub"), "shop": payload.get("shop")}
    return {
        "access_token": token_service.create_access_token(token_data),
        "refresh_token": token_service.create_refresh_token(token_data),
        "token_type": "bearer"
    }
