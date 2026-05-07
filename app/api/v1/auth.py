from fastapi import APIRouter, Request, Depends, HTTPException, Query
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.dependencies import get_db
from app.services.auth_service import auth_service
import urllib.parse

router = APIRouter()

@router.get("/install")
async def install(shop: str = Query(...)):
    """
    Step 1: Redirect to Shopify for installation.
    """
    # Validate shop domain format
    if not shop.endswith(".myshopify.com"):
        raise HTTPException(status_code=400, detail="Invalid shop domain")

    redirect_uri = f"{settings.APP_URL}/api/v1/auth/callback"
    scopes = settings.SHOPIFY_SCOPES
    
    install_url = (
        f"https://{shop}/admin/oauth/authorize?"
        f"client_id={settings.SHOPIFY_API_KEY}&"
        f"scope={scopes}&"
        f"redirect_uri={urllib.parse.quote(redirect_uri)}"
    )
    
    return RedirectResponse(url=install_url)

@router.get("/callback")
async def callback(
    request: Request,
    shop: str = Query(...),
    code: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    """
    Step 2: Handle callback, verify HMAC, exchange code for token.
    """
    # 1. Verify HMAC
    query_params = dict(request.query_params)
    if not auth_service.verify_hmac(query_params):
        raise HTTPException(status_code=401, detail="HMAC verification failed")

    # 2. Exchange code for permanent access token
    try:
        access_token = await auth_service.exchange_code_for_token(shop, code)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to exchange token: {str(e)}")

    # 3. Save merchant to DB
    await auth_service.save_merchant(db, shop, access_token)

    # 4. Redirect to frontend or Shopify Admin
    # For now, we'll just redirect to the Shopify Admin
    return RedirectResponse(url=f"https://{shop}/admin/apps/{settings.APP_NAME.replace(' ', '-').lower()}")
