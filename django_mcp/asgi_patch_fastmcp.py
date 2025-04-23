"""
django_mcp/asgi_patch_fastmcp.py
"""

from django.conf import settings
from mcp.server.fastmcp import FastMCP
from starlette.applications import Starlette
from starlette.requests import Request

from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport

from .log import logger
from .interop_django_fastapi import _interpolate_starlette_path_with_url_params
from .asgi_interceptors import make_intercept_sse_send


# Override FastMCP.sse_app() to support nested paths (e.g. /mcp/sse instead of /sse)
# This monkey patch addresses a limitation in modelcontextprotocol/python-sdk.
# Related issue: https://github.com/modelcontextprotocol/python-sdk/issues/412
# Source code reference (original method):
# https://github.com/modelcontextprotocol/python-sdk/blob/70115b99b3ee267ef10f61df21f73a93db74db03/src/mcp/server/fastmcp/server.py#L480
def FastMCP_sse_app_patch(_self: FastMCP, starlette_base_path: str):
    '''
    Patched version of FastMCP.sse_app to handle dynamic Starlette paths.

    Initializes the SseServerTransport and provides a custom `handle_sse`
    ASGI endpoint that intercepts the outgoing SSE 'endpoint' event
    to inject the correctly resolved message posting URL.
    '''

    # Initialize SseServerTransport
    sse = SseServerTransport(f'{starlette_base_path}/messages/')

    async def handle_sse(request: Request) -> None:
        # Calculate resolved message base URL inside the handler using Starlette path format
        try:
            resolved_message_base_url = _interpolate_starlette_path_with_url_params(starlette_base_path, request.path_params) + "/messages/"
        except KeyError:
            # Log error if path parameters cannot be resolved based on the route
            logger.error(
                f"Could not resolve path parameters for SSE connection: {request.url.path} "
                f"using template {starlette_base_path}"
            )
            raise Exception(
                f"Could not resolve path parameters for SSE connection: {request.url.path} "
                f"using template {starlette_base_path}"
            )
        logger.debug(f"Resolved message base URL for SSE: {resolved_message_base_url}")

        # Intercept the original ASGI send callable to be able to rewrite SSE payloads
        intercepted_send = make_intercept_sse_send(request._send, resolved_message_base_url)

        # Use the intercepted send when connecting
        async with sse.connect_sse(
            request.scope,
            request.receive,
            intercepted_send,
        ) as streams:
            await _self._mcp_server.run(
                streams[0],
                streams[1],
                _self._mcp_server.create_initialization_options(),
            )

    return (handle_sse, sse) # Return tuple as before