"""
django_mcp/asgi_patch_fastmcp.py

Patches FastMCP.sse_app to handle dynamic paths and ASGI connection details
"""

import contextvars
import typing

from django.conf import settings
from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.requests import Request

from .log import logger
from .interop_django_fastapi import _interpolate_starlette_path_with_url_params
from .asgi_interceptors import make_intercept_sse_send


# Context variable to store MCP path parameters captured during the ASGI SSE connection
mcp_connection_path_params: contextvars.ContextVar[dict[str, typing.Any] | None] = contextvars.ContextVar(
    "mcp_connection_path_params", default=None
)


# Override FastMCP.sse_app() to support nested paths (e.g. /mcp/sse instead of /sse)
# This monkey patch addresses a limitation in modelcontextprotocol/python-sdk.
# Related issue: https://github.com/modelcontextprotocol/python-sdk/issues/412
# Source code reference (original method):
# https://github.com/modelcontextprotocol/python-sdk/blob/70115b99b3ee267ef10f61df21f73a93db74db03/src/mcp/server/fastmcp/server.py#L480
def FastMCP_sse_app_patch(_self: FastMCP, starlette_base_path: str):
    '''
    Patched version of FastMCP.sse_app

    Initializes the SseServerTransport and provides a custom `handle_sse`
    ASGI endpoint that captures path parameters, stores them in Context,
    and intercepts the outgoing SSE 'endpoint' event to inject the correctly
    resolved message posting URL.
    '''

    # Initialize SseServerTransport - message URL here is just a template
    sse = SseServerTransport(f'{starlette_base_path}/messages/')

    async def handle_sse(request: Request) -> None:
        token = None  # Initialize token for context variable reset
        resolved_message_base_url = "" # Initialize to avoid potential UnboundLocalError in error logs

        # Step 1) Capture path parameters from the request and store them in Context
        try:
            # Extract path parameters from the request
            path_params = request.path_params

            # Calculate the actual message base URL using the captured parameters
            resolved_message_base_url = _interpolate_starlette_path_with_url_params(
                starlette_base_path, path_params
            ) + "/messages/"
            logger.debug(f"Resolved message base URL for SSE: {resolved_message_base_url}")

            # Set the context variable for the duration of this connection
            # so that URL params can be accessed by mcp.tool-decorated functions
            token = mcp_connection_path_params.set(path_params)
            logger.debug(f"Set mcp_connection_path_params: {path_params}")
        except Exception as e:
            logger.exception(f"Error processing path parameters or setting context var: {e}")
            # Reset context var if set before error occurred during setup
            if token:
                mcp_connection_path_params.reset(token)
            raise # Re-raise the exception

        # Step 2) Intercept the original ASGI send callable to be able to rewrite SSE payloads
        intercepted_send = make_intercept_sse_send(request._send, resolved_message_base_url)
        try:
            # Use the intercepted send when connecting
            async with sse.connect_sse(
                request.scope,
                request.receive,
                intercepted_send,
            ) as streams:
                # Run the MCP server loop
                await _self._mcp_server.run(
                    streams[0],
                    streams[1],
                    _self._mcp_server.create_initialization_options(),
                )
        finally:
            # Ensure the context variable is reset when the connection closes
            if token:
                mcp_connection_path_params.reset(token)
                logger.debug("Reset mcp_connection_path_params")

    # Return the handler and transport instance
    return (handle_sse, sse)
