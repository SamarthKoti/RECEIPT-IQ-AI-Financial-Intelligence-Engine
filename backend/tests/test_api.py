import io
from PIL import Image

def register(client, email='one@example.com'):
    return client.post('/api/auth/register', json={'name': 'Test User', 'email': email, 'password': 'test-only-long-password'})

def image_bytes():
    image = Image.new('RGB', (200, 300), 'white')
    output = io.BytesIO()
    image.save(output, format='PNG')
    return output.getvalue()

def upload(client, monkeypatch):
    import app.main as main
    monkeypatch.setattr(main, 'extract', lambda _: {'text': 'MARKET\n2026-10-10\nMilk 60.00\nSubtotal 60.00\nTotal 80.00', 'lines': [{'text': 'Milk 60.00', 'box': [0, 0, 1, .1], 'confidence': .9} for _ in range(5)], 'confidence': .9, 'warnings': []})
    response = client.post('/api/receipts/upload', files={'file': ('receipt.png', image_bytes(), 'image/png')})
    assert response.status_code == 201, response.text
    return response.json()

def test_authentication_and_logout(clients):
    a, b = clients
    assert a.get('/api/auth/me').status_code == 401
    response = register(a)
    assert response.status_code == 201
    assert 'HttpOnly' in response.headers['set-cookie']
    assert 'SameSite=lax' in response.headers['set-cookie']
    assert 'password_hash' not in response.json()
    assert register(b).status_code == 409
    assert a.get('/api/auth/me').json()['email'] == 'one@example.com'
    assert a.post('/api/auth/logout').status_code == 200
    assert a.get('/api/auth/me').status_code == 401
    assert a.post('/api/auth/login', json={'email': 'one@example.com', 'password': 'wrong'}).status_code == 401
    assert a.post('/api/auth/login', json={'email': 'ONE@example.com', 'password': 'test-only-long-password'}).status_code == 200

def test_csrf_and_validation(clients):
    a, _ = clients
    assert a.post('/api/auth/logout', headers={'X-Receipt-IQ': ''}).status_code == 403
    assert a.post('/api/auth/logout', headers={'Origin': 'https://attacker.example'}).status_code == 403
    assert a.post('/api/auth/register', json={'name': 'A', 'email': 'bad', 'password': 'short'}).status_code == 422

def test_eight_character_password_registration_and_login(clients):
    a, _ = clients
    payload = {'name': 'Password QA', 'email': 'eight@example.com', 'password': 'Eight123'}
    assert a.post('/api/auth/register', json={**payload, 'password': 'Seven12'}).status_code == 422
    assert a.post('/api/auth/register', json=payload).status_code == 201
    assert a.post('/api/auth/logout').status_code == 200
    assert a.post('/api/auth/login', json=payload).status_code == 200

def test_complete_receipt_review_investigation_report_and_isolation(clients, monkeypatch):
    a, b = clients
    register(a)
    register(b, 'two@example.com')
    receipt = upload(a, monkeypatch)
    rid = receipt['id']
    assert a.get('/api/analytics/overview').json()['total'] == '0'
    assert a.get(f'/api/receipts/{rid}/investigation').status_code == 409
    for path in [f'/api/receipts/{rid}', f'/api/receipts/{rid}/image', f'/api/receipts/{rid}/investigation', f'/api/reports/export?receipt_id={rid}']:
        assert b.get(path).status_code == 404
    assert b.post(f'/api/receipts/{rid}/confirm').status_code == 404
    receipt['category'] = 'Groceries'
    assert a.patch(f'/api/receipts/{rid}', json=receipt).status_code == 200
    assert a.post(f'/api/receipts/{rid}/confirm').status_code == 200
    findings = a.get(f'/api/receipts/{rid}/investigation').json()
    assert any(x['key'] == 'total' for x in findings['alerts'])
    assert a.patch(f'/api/receipts/{rid}/alerts/total', json={'action': 'expected'}).status_code == 200
    assert next(x for x in a.get(f'/api/receipts/{rid}/investigation').json()['alerts'] if x['key'] == 'total')['state'] == 'expected'
    assert a.get('/api/analytics/overview').json()['total'] == '80.00'
    assert a.get('/api/analytics/categories').json() == [{'name': 'Groceries', 'value': '80.00'}]
    assert a.get('/api/analytics/trends').json()[0]['month'] == '2026-10'
    report = a.get('/api/reports/export')
    assert report.status_code == 200 and 'expected' in report.text and 'MARKET' in report.text
    assert a.get(f'/api/receipts/{rid}/image').headers['content-type'] == 'image/png'
    assert b.get('/api/receipts').json() == []
    assert a.get('/api/analytics/details').json()['total'] == '80.00'
    assert b.get('/api/analytics/details').json()['count'] == 0
    assert a.get('/api/analytics/details?days=0').status_code == 422
    assert b.patch(f'/api/receipts/{rid}', json=receipt).status_code == 404
    # Editing invalidates confirmation and prior decisions.
    receipt['total'] = '60.00'
    assert a.patch(f'/api/receipts/{rid}', json=receipt).json()['status'] == 'review'
    assert a.get('/api/analytics/overview').json()['confirmed'] == 0

def test_upload_validation_duplicates_and_currency_scope(clients, monkeypatch):
    a, _ = clients
    register(a)
    assert a.post('/api/receipts/upload', files={'file': ('evil.png', b'not an image', 'image/png')}).status_code == 422
    assert a.post('/api/receipts/upload', files={'file': ('empty.png', b'', 'image/png')}).status_code == 400
    one, two = upload(a, monkeypatch), upload(a, monkeypatch)
    assert all(r['possible_duplicate'] for r in a.get('/api/receipts').json())
    a.post(f"/api/receipts/{one['id']}/confirm")
    a.post(f"/api/receipts/{two['id']}/confirm")
    assert any(x['key']=='duplicate-transaction' for x in a.get(f"/api/receipts/{two['id']}/investigation").json()['alerts'])
    assert a.patch('/api/auth/me', json={'name': 'Updated Name', 'currency': 'USD'}).status_code == 200
    assert a.get('/api/analytics/overview').json()['total'] == '0'
    assert a.get('/api/analytics/details').json()['count'] == 0

def test_confirm_requires_review_fields_and_valid_quantities(clients, monkeypatch):
    a, _ = clients
    register(a)
    receipt = upload(a, monkeypatch)
    receipt['items'][0]['quantity'] = '0'
    assert a.patch(f"/api/receipts/{receipt['id']}", json=receipt).status_code == 422
    receipt['items'] = []
    assert a.patch(f"/api/receipts/{receipt['id']}", json=receipt).status_code == 200
    assert a.post(f"/api/receipts/{receipt['id']}/confirm").status_code == 422
