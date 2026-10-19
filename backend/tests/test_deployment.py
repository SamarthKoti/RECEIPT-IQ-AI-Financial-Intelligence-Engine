from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient
from pydantic import SecretStr
import httpx
import pytest
from app.frontend import FrontendFiles
from app import object_storage
from test_api import register, upload


def test_spa_routes_do_not_expose_files_or_hide_api_errors(tmp_path):
    (tmp_path / 'index.html').write_text('<h1>Receipt IQ</h1>')
    (tmp_path / 'app.js').write_text('console.log(1)')
    app = FastAPI()
    app.mount('/', FrontendFiles(directory=tmp_path, html=True))
    with TestClient(app) as client:
        assert client.get('/login').status_code == 200
        assert client.get('/receipts/123').status_code == 200
        assert client.get('/app.js').status_code == 200
        for path in ['/api/missing', '/missing.js', '/.env', '/%2e%2e/private.txt']:
            assert client.get(path).status_code == 404


def test_cloud_storage_ownership_and_no_local_dependency(clients, monkeypatch):
    import app.main as main
    a, b = clients
    register(a)
    register(b, 'cloud-other@example.com')
    objects = {}
    monkeypatch.setattr(main.settings, 'storage_backend', 'supabase')
    monkeypatch.setattr(object_storage, 'upload_image', lambda path: objects.update({path.name: path.read_bytes()}))
    monkeypatch.setattr(object_storage, 'download_image', lambda name: objects[name])
    receipt = upload(a, monkeypatch)
    assert not list(main.storage.glob('*.png'))
    response = a.get(receipt['image_url'])
    assert response.status_code == 200 and response.content.startswith(b'\x89PNG')
    assert b.get(receipt['image_url']).status_code == 404


def test_cloud_upload_failure_does_not_save_receipt(clients, monkeypatch):
    import app.main as main
    from test_api import image_bytes
    a, _ = clients
    register(a)
    monkeypatch.setattr(main.settings, 'storage_backend', 'supabase')
    monkeypatch.setattr(main, 'extract', lambda _: {'text': '', 'lines': [], 'confidence': 0, 'warnings': []})
    def fail(_):
        raise HTTPException(503, 'Storage unavailable')
    monkeypatch.setattr(object_storage, 'upload_image', fail)
    assert a.post('/api/receipts/upload', files={'file': ('x.png', image_bytes())}).status_code == 503
    assert a.get('/api/receipts').json() == []
    assert not list(main.storage.glob('*.png'))


def test_storage_rejects_public_bucket_and_hides_provider_errors(monkeypatch):
    monkeypatch.setattr(object_storage.settings, 'supabase_url', 'https://project.example')
    monkeypatch.setattr(object_storage.settings, 'supabase_secret_key', SecretStr('sb_secret_test'))
    def mock(method, url, **kwargs):
        assert kwargs['headers']['apikey'] == 'sb_secret_test'
        return httpx.Response(200, json={'public': True}, request=httpx.Request(method, url))
    monkeypatch.setattr(httpx, 'request', mock)
    with pytest.raises(RuntimeError, match='private'):
        object_storage.check_private_bucket()
    def fail(*args, **kwargs):
        raise httpx.ConnectError('provider-secret-diagnostic')
    monkeypatch.setattr(httpx, 'request', fail)
    with pytest.raises(HTTPException) as exc:
        object_storage.download_image('a'*32+'.png')
    assert exc.value.status_code == 503
    assert 'provider-secret' not in exc.value.detail
    with pytest.raises(ValueError):
        object_storage.download_image('../private.png')
