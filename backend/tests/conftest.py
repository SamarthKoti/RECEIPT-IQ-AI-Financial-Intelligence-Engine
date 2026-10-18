import sys
from pathlib import Path
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from app.db import Base, get_db
from app.main import app, attempts
import app.main as main

@pytest.fixture
def clients(tmp_path, monkeypatch):
    engine = create_engine('sqlite://', connect_args={'check_same_thread': False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(engine, expire_on_commit=False)
    def database():
        with factory() as db:
            yield db
    app.dependency_overrides[get_db] = database
    monkeypatch.setattr(main, 'storage', tmp_path)
    attempts.clear()
    with TestClient(app, headers={'X-Receipt-IQ': '1'}) as a, TestClient(app, headers={'X-Receipt-IQ': '1'}) as b:
        for client in (a, b):
            client.headers['X-CSRF-Token'] = client.get('/api/auth/csrf').json()['csrf_token']
        yield a, b
    app.dependency_overrides.clear()
    engine.dispose()
