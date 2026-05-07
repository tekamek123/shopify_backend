from fastapi import APIRouter, Query, HTTPException, Depends
from fastapi.responses import RedirectResponse
import urllib.parse
from app.config import settings

router = APIRouter()

@router.get("/install")
async def install(shop: str = Query(...)):
    """
    Step 1: Validate shop parameter and redirect to Shopify OAuth.
    """
    # 1. Basic validation of the shop domain
    if not shop or not shop.endswith(".myshopify.com"):
        raise HTTPException(status_code=400, detail="Invalid shop domain. Must end with .myshopify.com")

    # 2. Build the authorization URL
    redirect_uri = f"{settings.APP_URL}/api/v1/auth/callback"
    scopes = settings.SHOPIFY_SCOPES
    
    params = {
        "client_id": settings.SHOPIFY_API_KEY,
        "scope": scopes,
        "redirect_uri": redirect_uri,
    }
    
    auth_url = f"https://{shop}/admin/oauth/authorize?{urllib.parse.urlencode(params)}"
    
    # 3. Redirect the merchant
    return RedirectResponse(url=auth_url)
