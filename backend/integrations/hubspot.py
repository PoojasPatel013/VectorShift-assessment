# hubspot.py
import datetime
import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import hashlib

import requests
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

CLIENT_ID = '2d1c2e87-4277-4736-aba3-3c319dfc21b0'  
CLIENT_SECRET = '5311f976-c540-465a-88e5-76515fd3785b'  
REDIRECT_URI = 'http://localhost:8000/integrations/hubspot/oauth2callback'
# HubSpot OAuth authorization URL
authorization_url = f'https://app-na2.hubspot.com/oauth/authorize?client_id={CLIENT_ID}&redirect_uri={REDIRECT_URI}&scope=crm.objects.contacts.read%20crm.objects.contacts.write'

encoded_client_id_secret = base64.b64encode(f'{CLIENT_ID}:{CLIENT_SECRET}'.encode()).decode()

async def authorize_hubspot(user_id, org_id):
    state_data = {
        'state': secrets.token_urlsafe(32),
        'user_id': user_id,
        'org_id': org_id
    }
    encoded_state = base64.urlsafe_b64encode(json.dumps(state_data).encode('utf-8')).decode('utf-8')

    auth_url = f'{authorization_url}&state={encoded_state}'
    await add_key_value_redis(f'hubspot_state:{org_id}:{user_id}', json.dumps(state_data), expire=600)

    return auth_url

async def oauth2callback_hubspot(request: Request):
    if request.query_params.get('error'):
        raise HTTPException(status_code=400, detail=request.query_params.get('error_description'))
    code = request.query_params.get('code')
    encoded_state = request.query_params.get('state')
    state_data = json.loads(base64.urlsafe_b64decode(encoded_state).decode('utf-8'))

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'hubspot_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        # Exchange authorization code for access token
        response = await client.post(
            'https://api.hubapi.com/oauth/v1/token',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'redirect_uri': REDIRECT_URI,
                'client_id': CLIENT_ID,
                'client_secret': CLIENT_SECRET
            },
            headers={
                'Content-Type': 'application/x-www-form-urlencoded',
            }
        )

    await add_key_value_redis(f'hubspot_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_hubspot_credentials(user_id, org_id):
    credentials = await get_value_redis(f'hubspot_credentials:{org_id}:{user_id}')
    return credentials

async def create_integration_item_metadata_object(response_json, item_type, parent_id=None, parent_name=None):
    return IntegrationItem(
        id=response_json.get('id'),
        name=response_json.get('properties', {}).get('firstname', '') + ' ' + response_json.get('properties', {}).get('lastname', ''),
        type=item_type,
        parent_id=parent_id,
        parent_name=parent_name,
        properties=response_json.get('properties', {})
    )

async def get_items_hubspot(credentials):
    if not credentials:
        return []

    access_token = json.loads(credentials).get('access_token')
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        # First get all contacts
        contacts_response = await client.get(
            'https://api.hubapi.com/crm/v3/objects/contacts',
            headers=headers
        )
        
        items = []
        
        if contacts_response.status_code == 200:
            contacts = contacts_response.json().get('results', [])
            for contact in contacts:
                contact_id = contact.get('id')
                contact_data = contact.get('properties', {})
                
                # Get contact details
                contact_response = await client.get(
                    f'https://api.hubapi.com/crm/v3/objects/contacts/{contact_id}',
                    headers=headers
                )
                
                if contact_response.status_code == 200:
                    contact_details = contact_response.json()
                    items.append(await create_integration_item_metadata_object(
                        {
                            'id': contact_id,
                            'name': contact_data.get('firstname', '') + ' ' + contact_data.get('lastname', ''),
                            'email': contact_data.get('email', ''),
                            'phone': contact_data.get('phone', ''),
                            'properties': contact_details,
                            'url': f'https://app.hubspot.com/contacts/{contact_id}'
                        },
                        'contact',
                        None,
                        None
                    ))
        
        # Get companies
        companies_response = await client.get(
            'https://api.hubapi.com/crm/v3/objects/companies',
            headers=headers
        )
        
        if companies_response.status_code == 200:
            companies = companies_response.json().get('results', [])
            for company in companies:
                company_id = company.get('id')
                company_data = company.get('properties', {})
                
                # Get company details
                company_response = await client.get(
                    f'https://api.hubapi.com/crm/v3/objects/companies/{company_id}',
                    headers=headers
                )
                
                if company_response.status_code == 200:
                    company_details = company_response.json()
                    items.append(await create_integration_item_metadata_object(
                        {
                            'id': company_id,
                            'name': company_data.get('name', ''),
                            'domain': company_data.get('domain', ''),
                            'properties': company_details,
                            'url': f'https://app.hubspot.com/companies/{company_id}'
                        },
                        'company',
                        None,
                        None
                    ))
        
        return items
    return []