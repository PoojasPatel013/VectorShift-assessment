# airtable.py

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



async def authorize_airtable(user_id, org_id):
    credentials = {
        'pat': PAT,
        'base_id': BASE_ID
    }
    await add_key_value_redis(f'airtable_credentials:{org_id}:{user_id}', json.dumps(credentials), expire=600)
    
    return {'success': True}

async def oauth2callback_airtable(request: Request):
    pass

    await add_key_value_redis(f'airtable_credentials:{org_id}:{user_id}', json.dumps(response.json()), expire=600)
    
    close_window_script = """
    <html>
        <script>
            window.close();
        </script>
    </html>
    """
    return HTMLResponse(content=close_window_script)

async def get_airtable_credentials(user_id, org_id):
    credentials = await get_value_redis(f'airtable_credentials:{org_id}:{user_id}')
    if not credentials:
        return None
    return json.loads(credentials)

async def create_integration_item_metadata_object(response_json, item_type, parent_id=None, parent_name=None):
    if item_type == 'record':
        name = response_json.get('fields', {}).get('Name', '') or f"Record {response_json.get('id')}"
        
        fields = response_json.get('fields', {})
        
        properties = {
            'id': response_json.get('id'),
            'table': response_json.get('table_name', 'Table 1'),
            'fields': fields,
            'createdTime': response_json.get('createdTime'),
            'url': f'https://airtable.com/tbl{response_json.get("table_id", "")}/rec{response_json.get("id", "")}'
        }
    else:
        name = response_json.get('name', '')
        properties = response_json
    
    return IntegrationItem(
        id=response_json.get('id'),
        name=name,
        type=item_type,
        parent_id=parent_id,
        parent_name=parent_name,
        properties=properties
    )

async def fetch_items(base_id: str, pat: str, aggregated_response: list, offset=None):
    headers = {
        'Authorization': f'Bearer {pat}',
        'Content-Type': 'application/json'
    }
    
    # Get tables from Airtable Meta API
    tables_url = f'https://api.airtable.com/v0/meta/bases/{base_id}/tables'
    async with httpx.AsyncClient() as client:
        tables_response = await client.get(tables_url, headers=headers)
        
    if tables_response.status_code == 200:
        tables = tables_response.json().get('tables', [])
        
        for table in tables:
            table_id = table.get('id')
            table_name = table.get('name')
            
            # Get records from specific table
            records_url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
            response = await client.get(
                records_url,
                headers=headers,
                params={'offset': offset} if offset else None
            )
            
            if response.status_code == 200:
                records = response.json().get('records', [])
                for record in records:
                    # Add table information to each record
                    record['table_name'] = table_name
                    record['table_id'] = table_id
                    aggregated_response.append(record)
                
                offset = response.json().get('offset')
                if offset:
                    await fetch_items(base_id, pat, aggregated_response, offset)
    
    return aggregated_response

async def get_items_airtable(credentials):
    if not credentials:
        return []

    base_id = credentials.get('base_id')
    pat = credentials.get('pat')
    
    aggregated_response = []
    await fetch_items(base_id, pat, aggregated_response)
    
    return [await create_integration_item_metadata_object(
        record,
        'record',
        None,
        None
    ) for record in aggregated_response]
    
    if tables_response.status_code == 200:
        tables_response = tables_response.json()
        for table in tables_response['tables']:
            list_of_integration_item_metadata.append(
                create_integration_item_metadata_object(
                    table,
                        'Table',
                        response.get('id', None),
                        response.get('name', None),
                    )
                )

    print(f'list_of_integration_item_metadata: {list_of_integration_item_metadata}')
    return list_of_integration_item_metadata
