"""Fail closed on an incomplete free-host deployment; migrate before serving."""
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
os.chdir(ROOT)
sys.path.insert(0, str(ROOT / 'backend'))
# Render assigns this trusted deployment variable; never derive origins from Host headers.
if not os.getenv('FRONTEND_ORIGINS') and os.getenv('RENDER_EXTERNAL_URL'):
    import json
    os.environ['FRONTEND_ORIGINS'] = json.dumps([os.environ['RENDER_EXTERNAL_URL'].rstrip('/')])

from app.config import settings
from app.object_storage import check_private_bucket

if not settings.cookie_secure or any(not o.startswith('https://') for o in settings.allowed_origins):
    raise RuntimeError('Production requires secure cookies and exact HTTPS frontend origins.')
if not settings.database_url.startswith('postgresql+psycopg://'):
    raise RuntimeError('Free-host deployment requires persistent PostgreSQL, not ephemeral SQLite.')
if settings.storage_backend != 'supabase':
    raise RuntimeError('Free-host deployment requires private persistent Supabase storage.')
check_private_bucket()
subprocess.run([sys.executable, '-m', 'alembic', '-c', 'backend/alembic.ini', 'upgrade', 'head'], check=True)

# This application owns its tables and authenticates requests itself, not through
# Supabase Auth. Block direct Data API access, including password/session tables.
from sqlalchemy import text
from app.db import engine
from app.models import Base
with engine.begin() as connection:
    for table in list(Base.metadata.tables) + ['alembic_version']:
        quoted = connection.dialect.identifier_preparer.quote(table)
        connection.execute(text(f'ALTER TABLE public.{quoted} ENABLE ROW LEVEL SECURITY'))
        connection.execute(text(f'REVOKE ALL ON public.{quoted} FROM anon, authenticated'))

os.execvp(sys.executable, [sys.executable, '-m', 'uvicorn', 'app.main:app', '--host', '0.0.0.0', '--port', os.environ.get('PORT', '10000'), '--workers', '1'])
