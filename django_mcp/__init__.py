import asyncio
import random
from django.conf import settings
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.routing import Mount, Route
from starlette.types import ASGIApp

# Initialize FastMCP app for handling key routes like /sse, /messages, etc.
mcp_app = FastMCP()

# Override FastMCP.sse_app() to support nested paths (e.g. /mcp/sse instead of /sse)
# This monkey patch addresses a limitation in modelcontextprotocol/python-sdk.
# Related issue: https://github.com/modelcontextprotocol/python-sdk/issues/412
# Source code reference (original method):
# https://github.com/modelcontextprotocol/python-sdk/blob/70115b99b3ee267ef10f61df21f73a93db74db03/src/mcp/server/fastmcp/server.py#L480
def FastMCP_sse_app_patch(_self: FastMCP, base_path: str = '/mcp'):
    sse = SseServerTransport(f'{base_path}/messages/')

    async def handle_sse(request: Request) -> None:
        async with sse.connect_sse(
            request.scope,
            request.receive,
            request._send,  # type: ignore[reportPrivateUsage]
        ) as streams:
            await _self._mcp_server.run(
                streams[0],
                streams[1],
                _self._mcp_server.create_initialization_options(),
            )

    return (handle_sse, sse)

def apply_django_settings(_self: FastMCP):
    _self._mcp_server.title = settings.MCP_SERVER_TITLE
    _self._mcp_server.instructions = settings.MCP_SERVER_INSTRUCTIONS
    _self._mcp_server.version = settings.MCP_SERVER_VERSION

# Create a combined Starlette app with Django and MCP mounted
def mount_mcp_server(django_http_app: ASGIApp, mcp_base_path: str = '/mcp') -> ASGIApp:
    # Apply project settings.py overrides to the MCP application
    apply_django_settings(mcp_app)

    # Patch the FastMCP.sse_app() method to support nested paths
    (handle_sse, sse) = FastMCP_sse_app_patch(mcp_app, base_path=mcp_base_path)

    # Register the patched SSE handler and mount the messages endpoint
    combined_app = Starlette(routes=[
        Route(f'{mcp_base_path}/sse', endpoint=handle_sse),
        Mount(f'{mcp_base_path}/messages/', app=sse.handle_post_message),
        Mount('/', app=django_http_app),
    ])

    return combined_app
