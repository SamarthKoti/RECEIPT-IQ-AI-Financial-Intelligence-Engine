"""Serve built React routes from the same origin as the private API."""
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException


class FrontendFiles(StaticFiles):
    async def get_response(self, path, scope):
        route_path = path.replace('\\', '/').lstrip('/')
        if route_path == 'api' or route_path.startswith('api/'):
            raise HTTPException(404)
        try:
            return await super().get_response(path, scope)
        except HTTPException as exc:
            # Only extensionless client routes receive the SPA fallback.
            if exc.status_code != 404 or '.' in path or scope['method'] not in ('GET', 'HEAD'):
                raise
            return await super().get_response('index.html', scope)
