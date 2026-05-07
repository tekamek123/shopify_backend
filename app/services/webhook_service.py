from app.services.shopify_client import ShopifyClient
from app.config import settings
from typing import List

class WebhookService:
    MANDATORY_TOPICS = [
        "ORDERS_CREATE",
        "ORDERS_UPDATED",
        "PRODUCTS_UPDATE",
        "APP_UNINSTALLED"
    ]

    async def register_webhooks(self, shop_domain: str, access_token: str):
        """
        Register mandatory webhooks for a shop.
        """
        client = ShopifyClient(shop_domain, access_token)
        callback_url = f"{settings.APP_URL}/api/v1/webhooks"
        
        for topic in self.MANDATORY_TOPICS:
            mutation = """
            mutation webhookSubscriptionCreate($topic: WebhookSubscriptionTopic!, $webhookSubscription: WebhookSubscriptionInput!) {
              webhookSubscriptionCreate(topic: $topic, webhookSubscription: $webhookSubscription) {
                userErrors {
                  field
                  message
                }
                webhookSubscription {
                  id
                }
              }
            }
            """
            variables = {
                "topic": topic,
                "webhookSubscription": {
                    "callbackUrl": f"{callback_url}/{topic.lower().replace('_', '/')}",
                    "format": "JSON"
                }
            }
            
            try:
                result = await client.graphql(mutation, variables)
                errors = result.get("data", {}).get("webhookSubscriptionCreate", {}).get("userErrors", [])
                if errors:
                    print(f"Errors registering webhook {topic}: {errors}")
                else:
                    print(f"Successfully registered webhook: {topic}")
            except Exception as e:
                print(f"Failed to register webhook {topic}: {str(e)}")

webhook_service = WebhookService()
