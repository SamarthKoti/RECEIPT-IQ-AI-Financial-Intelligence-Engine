import pytest
from sqlalchemy import select
from app.db import get_db
from app.main import app
from app.models import User
from app.security import password_hasher

ORIGINS = [
    'http://localhost:5173', 'http://127.0.0.1:5173',
    'http://localhost:5174', 'http://127.0.0.1:5174',
]


@pytest.mark.parametrize('origin', ORIGINS)
def test_complete_authentication_for_each_origin(clients, origin):
    client, _ = clients
    client.headers['Origin'] = origin
    preflight = client.options('/api/auth/register', headers={
        'Access-Control-Request-Method': 'POST',
        'Access-Control-Request-Headers': 'content-type,x-receipt-iq,x-csrf-token',
    })
    assert preflight.status_code == 200
    assert preflight.headers['access-control-allow-origin'] == origin
    assert preflight.headers['access-control-allow-credentials'] == 'true'
    bootstrap = client.get('/api/auth/csrf')
    assert bootstrap.headers['cache-control'] == 'no-store'
    assert 'HttpOnly' in bootstrap.headers['set-cookie']
    token = bootstrap.json()['csrf_token']
    assert token == client.cookies['receipt_csrf']
    client.headers['X-CSRF-Token'] = token
    payload = {'name': 'Origin QA', 'email': 'origin@example.com', 'password': 'test-only-valid-password'}
    registration = client.post('/api/auth/register', json=payload)
    assert registration.status_code == 201, registration.text
    assert registration.headers['access-control-allow-origin'] == origin
    assert 'receipt_session' in client.cookies
    database = app.dependency_overrides[get_db]()
    db = next(database)
    try:
        stored = db.scalar(select(User).where(User.email == payload['email']))
        assert stored is not None
        assert stored.password_hash != payload['password']
        assert password_hasher.verify(payload['password'], stored.password_hash)
    finally:
        database.close()
    assert client.get('/api/auth/me').json()['email'] == payload['email']
    assert client.get('/api/analytics/overview').status_code == 200
    assert client.post('/api/auth/logout').status_code == 200
    assert client.get('/api/auth/me').status_code == 401
    assert client.post('/api/auth/login', json=payload).status_code == 200
    assert client.get('/api/analytics/overview').status_code == 200


@pytest.mark.parametrize('origin', ['http://localhost:5175', 'http://127.0.0.1:5174.evil.test', 'https://evil.test', 'null'])
def test_untrusted_origins_remain_rejected(clients, origin):
    client, _ = clients
    client.headers['Origin'] = origin
    assert client.get('/api/auth/csrf').status_code == 403
    response = client.post('/api/auth/logout')
    assert response.status_code == 403
    assert response.json()['code'] == 'origin_invalid'
    assert 'access-control-allow-origin' not in response.headers
    assert client.options('/api/auth/register', headers={'Access-Control-Request-Method': 'POST'}).status_code == 400


def test_tokens_are_random_cookie_bound_and_required(clients):
    a, b = clients
    a.headers['Origin'] = ORIGINS[0]
    original = a.headers['X-CSRF-Token']
    assert original != b.headers['X-CSRF-Token']
    assert a.get('/api/auth/csrf').json()['csrf_token'] == original
    for token in ('', '1', b.headers['X-CSRF-Token']):
        response = a.post('/api/auth/logout', headers={'X-CSRF-Token': token})
        assert response.status_code == 403
        assert response.json()['code'] == 'csrf_invalid'
        # CORS must wrap security failures, not hide them from trusted clients.
        assert response.headers['access-control-allow-origin'] == ORIGINS[0]
    a.cookies.clear()
    assert a.post('/api/auth/logout').status_code == 403
    replacement = a.get('/api/auth/csrf').json()['csrf_token']
    assert replacement != original
    a.headers['X-CSRF-Token'] = replacement
    assert a.post('/api/auth/logout').status_code == 200
