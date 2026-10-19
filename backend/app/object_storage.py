"""Private receipt storage. Credentials never leave the backend."""
import re
from pathlib import Path
import httpx
from fastapi import HTTPException
from .config import settings


def request(method, suffix, **kwargs):
    if not settings.supabase_url or not settings.supabase_secret_key:
        raise RuntimeError('Supabase storage configuration is incomplete.')
    key = settings.supabase_secret_key.get_secret_value()
    headers = {'apikey': key}
    # Legacy JWT keys need Authorization; new sb_secret keys use apikey.
    if not key.startswith('sb_secret_'):
        headers['Authorization'] = f'Bearer {key}'
    headers.update(kwargs.pop('headers', {}))
    try:
        response = httpx.request(method, f'{settings.supabase_url.rstrip("/")}/storage/v1/{suffix}', headers=headers, timeout=60, **kwargs)
        response.raise_for_status()
        return response
    except httpx.HTTPError:
        # Do not expose provider response bodies, credentials, or URLs.
        raise HTTPException(503, 'Receipt storage is temporarily unavailable. Please try again.') from None


def object_path(name):
    if not re.fullmatch(r'[0-9a-f]{32}\.png', name):
        raise ValueError('Invalid receipt storage name.')
    if not re.fullmatch(r'[a-zA-Z0-9_-]+', settings.supabase_bucket):
        raise ValueError('Invalid storage bucket name.')
    return f'{settings.supabase_bucket}/{name}'


def check_private_bucket():
    object_path('0' * 32 + '.png')
    bucket = request('GET', f'bucket/{settings.supabase_bucket}').json()
    if bucket.get('public') is not False:
        raise RuntimeError('Receipt storage bucket must be private.')


def upload_image(path: Path):
    request('POST', f'object/{object_path(path.name)}', content=path.read_bytes(), headers={'Content-Type': 'image/png', 'x-upsert': 'false'})


def download_image(name):
    return request('GET', f'object/authenticated/{object_path(name)}').content


def remove_image(name):
    object_path(name)
    request('DELETE', f'object/{settings.supabase_bucket}', json={'prefixes': [name]})
