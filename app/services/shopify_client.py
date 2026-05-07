import httpx
import asyncio
import time
from typing import Dict, Any, Optional
from app.config import settings

class ShopifyClient:
    def __init__(self, shop_domain: str, access_token: str):
        self.shop_domain = shop_domain
        self.access_token = access_token
        self.base_url = f"https://{shop_domain}/admin/api/{settings.SHOPIFY_API_VERSION}"
        self.headers = {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json",
        }

    async def _request(
        self, 
        method: str, 
        path: str, 
        json: Optional[Dict[str, Any]] = None, 
        params: Optional[Dict[str, Any]] = None,
        max_retries: int = 3
    ) -> httpx.Response:
        url = f"{self.base_url}/{path}"
        
        async with httpx.AsyncClient() as client:
            for attempt in range(max_retries):
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=json,
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 429:
                    retry_after = float(response.headers.get("Retry-After", 2.0))
                    print(f"Shopify rate limit hit. Retrying after {retry_after} seconds...")
                    await asyncio.sleep(retry_after)
                    continue
                
                response.raise_for_status()
                return response
            
            # If we exhausted retries
            raise Exception(f"Max retries exceeded for Shopify API: {url}")

    async def graphql(self, query: str, variables: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        """
        path = "graphql.json"
        payload = {"query": query, "variables": variables or {}}
        response = await self._request("POST", path, json=payload)
        return response.json()

    async def rest_get(self, path: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute a REST GET request.
        """
        response = await self._request("GET", f"{path}.json", params=params)
        return response.json()

    async def rest_post(self, path: str, json: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a REST POST request.
        """
        response = await self._request("POST", f"{path}.json", json=json)
        return response.json()
