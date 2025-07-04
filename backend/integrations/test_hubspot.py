import asyncio
from hubspot import authorize_hubspot, oauth2callback_hubspot, get_items_hubspot
from redis_client import add_key_value_redis, get_value_redis

async def test_hubspot_integration():
    # Test authorization
    print("\nTesting HubSpot Authorization...")
    auth_url = await authorize_hubspot("test_user", "test_org")
    print(f"Authorization URL: {auth_url}")

    # Test OAuth callback
    print("\nTesting OAuth Callback...")
    # Simulate OAuth callback with test credentials
    test_credentials = {
        "access_token": "test_access_token",
        "refresh_token": "test_refresh_token",
        "expires_in": 3600,
        "token_type": "Bearer"
    }
    await add_key_value_redis("hubspot_credentials:test_org:test_user", json.dumps(test_credentials), expire=600)
    
    # Test getting items
    print("\nTesting Getting Items...")
    items = await get_items_hubspot(test_credentials)
    print(f"Retrieved {len(items)} items")
    
    if items:
        print("\nSample item:")
        print(items[0])

if __name__ == "__main__":
    asyncio.run(test_hubspot_integration())
