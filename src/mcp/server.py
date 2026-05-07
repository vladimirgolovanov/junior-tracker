from starlette.applications import Starlette

from src.mcp.auth import MCPBearerAuthMiddleware
from src.mcp.tools import mcp


def build_mcp_asgi_app() -> Starlette:
    asgi_app = mcp.streamable_http_app()
    asgi_app.add_middleware(MCPBearerAuthMiddleware)
    return asgi_app
