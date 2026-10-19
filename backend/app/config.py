from pathlib import Path
from urllib.parse import urlsplit
from pydantic import field_validator, SecretStr
from typing import Literal
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    database_url: str = 'sqlite:///./data/receipt_iq.db'
    storage_dir: str = './data/uploads'
    frontend_origin: str = 'http://127.0.0.1:5173'
    frontend_origins: list[str] | None = None
    cookie_secure: bool = False
    session_hours: int = 24
    tesseract_cmd: str | None = None
    storage_backend: Literal['local', 'supabase'] = 'local'
    supabase_url: str | None = None
    supabase_secret_key: SecretStr | None = None
    supabase_bucket: str = 'receipts'
    serve_frontend: bool = False
    model_config = SettingsConfigDict(env_file=PROJECT_ROOT / '.env', extra='ignore')

    @field_validator('frontend_origin')
    @classmethod
    def validate_origin(cls, value):
        origin = urlsplit(value)
        if '*' in value or origin.scheme not in ('http', 'https') or not origin.hostname or origin.username or origin.password or origin.path or origin.query or origin.fragment:
            raise ValueError('Use an exact HTTP(S) origin without a path, credentials, or wildcard.')
        return value

    @field_validator('frontend_origins')
    @classmethod
    def validate_origins(cls, values):
        if values is not None:
            if not values:
                raise ValueError('At least one frontend origin is required.')
            return list(dict.fromkeys(cls.validate_origin(value) for value in values))
        return values

    @property
    def allowed_origins(self):
        # Explicit plural setting takes precedence; keep existing deployments compatible.
        return self.frontend_origins if self.frontend_origins is not None else [self.frontend_origin]

    @field_validator('database_url')
    @classmethod
    def resolve_database(cls, value):
        if value.startswith('sqlite:///'):
            location = value.removeprefix('sqlite:///')
            if location != ':memory:':
                path = Path(location)
                if not path.is_absolute():
                    path = PROJECT_ROOT / path
                return 'sqlite:///' + path.resolve().as_posix()
        return value

    @field_validator('storage_dir')
    @classmethod
    def resolve_storage(cls, value):
        path = Path(value)
        return str((PROJECT_ROOT / path).resolve() if not path.is_absolute() else path.resolve())


settings = Settings()
