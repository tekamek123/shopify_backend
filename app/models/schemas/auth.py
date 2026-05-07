from pydantic import BaseModel

class TokenRequest(BaseModel):
    shop: str
    # In a real app, you'd send an authorization code here that was 
    # passed back to the app after the OAuth redirect.
    # For now, we'll assume the app sends the shop name.
    
class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
