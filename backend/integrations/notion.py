# notion.py

import json
import secrets
from fastapi import Request, HTTPException
from fastapi.responses import HTMLResponse
import httpx
import asyncio
import base64
import requests
from integrations.integration_item import IntegrationItem

from redis_client import add_key_value_redis, get_value_redis, delete_key_redis

INTEGRATION_TOKEN = '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'

NOTION_API_VERSION = '2023-08-01'

NOTION_API_URL = 'https://api.notion.com/v1'

async def authorize_notion(user_id, org_id):
    
    credentials = {
        'integration_token': INTEGRATION_TOKEN
    }
    await add_key_value_redis(f'notion_credentials:{org_id}:{user_id}', json.dumps(credentials), expire=600)
    
    return {'success': True}

async def oauth2callback_notion(request: Request):
    pass
    encoded_state = request.query_params.get('state')
    state_data = json.loads(encoded_state)

    original_state = state_data.get('state')
    user_id = state_data.get('user_id')
    org_id = state_data.get('org_id')

    saved_state = await get_value_redis(f'notion_state:{org_id}:{user_id}')

    if not saved_state or original_state != json.loads(saved_state).get('state'):
        raise HTTPException(status_code=400, detail='State does not match.')

    async with httpx.AsyncClient() as client:
        response, _ = await asyncio.gather(
            client.post(
                'https://api.notion.com/v1/oauth/token',
                json={
                    'grant_type': 'authorization_code',
                    'code': code,
                    'redirect_uri': REDIRECT_URI
                }, 
                headers={
                    'Authorization': f'Basic {encoded_client_id_secret}',
                    'Content-Type': 'application/json',
                }
            ),
            delete_key_redis(f'notion_state:{org_id}:{user_id}'),
        )

    await add_key_value_redis(f'notion_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_notion_credentials(user_id, org_id):
    credentials = await get_value_redis(f'notion_credentials:{org_id}:{user_id}')
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    credentials = json.loads(credentials)
    if not credentials:
        raise HTTPException(status_code=400, detail='No credentials found.')
    await delete_key_redis(f'notion_credentials:{org_id}:{user_id}')

    return credentials

def _recursive_dict_search(data, target_key):
    if target_key in data:
        return data[target_key]

    for value in data.values():
        if isinstance(value, dict):
            result = _recursive_dict_search(value, target_key)
            if result is not None:
                return result
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    result = _recursive_dict_search(item, target_key)
                    if result is not None:
                        return result
    return None

def create_integration_item_metadata_object(
    response_json: str,
) -> IntegrationItem:
    name = _recursive_dict_search(response_json['properties'], 'content')
    parent_type = (
        ''
        if response_json['parent']['type'] is None
        else response_json['parent']['type']
    )
    if response_json['parent']['type'] == 'workspace':
        parent_id = None
    else:
        parent_id = (
            response_json['parent'][parent_type]
        )

    name = _recursive_dict_search(response_json, 'content') if name is None else name
    name = 'multi_select' if name is None else name
    name = response_json['object'] + ' ' + name

    integration_item_metadata = IntegrationItem(
        id=response_json['id'],
        type=response_json['object'],
        name=name,
        creation_time=response_json['created_time'],
        last_modified_time=response_json['last_edited_time'],
        parent_id=parent_id,
    )

    return integration_item_metadata

async def get_items_notion(credentials):
    if not credentials:
        return []

    integration_token = credentials.get('integration_token')
    headers = {
        'Authorization': f'Bearer {integration_token}',
        'Notion-Version': NOTION_API_VERSION,
        'Content-Type': 'application/json'
    }
    
    async with httpx.AsyncClient() as client:
        databases_url = f'{NOTION_API_URL}/search'
        response = await client.post(
            databases_url,
            headers=headers,
            json={
                'filter': {
                    'property': 'object',
                    'value': 'database'
                }
            }
        )
        
    if response.status_code == 200:
        results = response.json().get('results', [])
        items = []
        
        for database in results:
            database_id = database.get('id')
            database_name = database.get('title', [{}])[0].get('plain_text', '')
            
            entries_url = f'{NOTION_API_URL}/databases/{database_id}/query'
            entries_response = await client.post(
                entries_url,
                headers=headers,
                json={}
            )
            
            if entries_response.status_code == 200:
                entries = entries_response.json().get('results', [])
                for entry in entries:
                    items.append(await create_integration_item_metadata_object(
                        {
                            'id': entry.get('id'),
                            'name': entry.get('properties', {}).get('Name', {}).get('title', [{}])[0].get('plain_text', ''),
                            'database': database_name,
                            'database_id': database_id,
                            'properties': entry.get('properties', {}),
                            'url': f'https://www.notion.so/{entry.get("id")}'
                        },
                        'notion_item',
                        None,
                        None
                    ))
        
        return items
    return []
