"""
django_mcp/mcp_sdk_patches.py

Monkey-patches for the mcp-python-sdk library
"""

import functools
import logging
from mcp.server.fastmcp import FastMCP, Context as BaseContext
from mcp.server.lowlevel.server import RequestContext

from .asgi_patch_fastmcp import mcp_connection_path_params  # ContextVar
from .context import DjangoMCPContext  # Custom Context class
from .decorators import log_mcp_tool_calls

logger = logging.getLogger(__name__)


def patch_mcp_tool_decorator(mcp_app: FastMCP):
    """Patches the MCP tool decorator to add logging."""
    original_tool_decorator_factory = mcp_app.tool
    logger.debug("Patching mcp_app.tool")

    def patched_tool_decorator_factory(*args, **kwargs):
        """The factory for the patched decorator."""
        inner_sdk_decorator = original_tool_decorator_factory(*args, **kwargs)
        def combined_decorator(func):
            """The combined decorator applying logging."""
            logged_func = log_mcp_tool_calls(func)
            return inner_sdk_decorator(logged_func)
        return combined_decorator

    mcp_app.tool = patched_tool_decorator_factory
    logger.info("Applied monkey patch to mcp_app.tool to automatically log tool calls. This can be disabled by setting MCP_PATCH_SDK_TOOL_LOGGING=False in settings.py.")


def patch_mcp_get_context(mcp_app: FastMCP):
    """
    Patches the FastMCP.get_context method to inject URL path parameters
    """
    original_get_context = mcp_app.get_context
    logger.debug("Patching FastMCP.get_context")

    @functools.wraps(original_get_context)
    def patched_get_context(self: FastMCP) -> DjangoMCPContext:
        """Patched version of get_context."""
        if not self._mcp_server:
            logger.warning("FastMCP._mcp_server is None during get_context call.")

        # The request_context is set by the low-level server for the current request
        request_context: RequestContext | None = self._mcp_server.request_context if self._mcp_server else None

        if request_context is None:
            logger.error("Could not retrieve RequestContext during get_context call.")
            path_params = None
        else:
            # Retrieve path parameters stored during SSE connection setup
            # Provide a default of None if the ContextVar is not set
            path_params = mcp_connection_path_params.get(None)

        logger.debug(f"Injecting path_params into context: {path_params}")

        custom_context = DjangoMCPContext(
            request_context=request_context, # Pass the (potentially None) request context
            fastmcp=self,  # Pass the FastMCP instance
            path_params=path_params,  # Pass the retrieved path parameters
        )
        return custom_context

    # Apply the patch
    mcp_app.get_context = patched_get_context.__get__(mcp_app, FastMCP)
    logger.info("FastMCP.get_context patched successfully to use DjangoMCPContext.")

