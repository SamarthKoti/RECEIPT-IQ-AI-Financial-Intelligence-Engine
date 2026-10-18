from app.config import Settings, PROJECT_ROOT
import pytest
from pydantic import ValidationError


def test_relative_paths_do_not_depend_on_launch_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    settings = Settings(_env_file=None, database_url='sqlite:///./data/receipt_iq.db', storage_dir='./data/uploads')
    assert settings.database_url == 'sqlite:///' + (PROJECT_ROOT / 'data/receipt_iq.db').as_posix()
    assert settings.storage_dir == str(PROJECT_ROOT / 'data/uploads')


def test_non_file_database_urls_are_preserved():
    assert Settings(_env_file=None, database_url='sqlite:///:memory:').database_url == 'sqlite:///:memory:'
    url = 'postgresql+psycopg://test:example@localhost/test'
    assert Settings(_env_file=None, database_url=url).database_url == url


def test_explicit_origins_override_legacy_single_origin():
    settings = Settings(_env_file=None, frontend_origin='https://legacy.example', frontend_origins=['https://app.example'])
    assert settings.allowed_origins == ['https://app.example']
    assert Settings(_env_file=None, frontend_origins=None).allowed_origins == ['http://127.0.0.1:5173']


@pytest.mark.parametrize('origin', ['*', 'https://*.example.com', 'https://app.example/path', 'https://user:pass@app.example', 'null'])
def test_origin_configuration_rejects_unsafe_values(origin):
    with pytest.raises(ValidationError):
        Settings(_env_file=None, frontend_origins=[origin])
