"""
django_mcp/context.py

Defines a custom MCP Context class for django-mcp.
"""

from typing import Any

from pydantic import Field
from mcp.server.fastmcp import Context as BaseContext
from mcp.server.fastmcp.server import FastMCP
from mcp.server.lowlevel.server import RequestContext


class DjangoMCPContext(BaseContext):
    """
    Custom MCP Context that includes path parameters from the initial ASGI connection.
    Inherits from Pydantic BaseModel via BaseContext.
    """
    # Declare path_params as a Pydantic Field to integrate with BaseModel validation/serialization
    path_params: dict[str, Any] = Field(default_factory=dict)

    def __init__(
        self,
        *,
        request_context: RequestContext | None = None,
        fastmcp: FastMCP | None = None,
        path_params: dict[str, Any] | None = None,
        **kwargs: Any,
    ):
        """
        Initialize the context.

        Args:
            request_context: The low-level MCP request context.
            fastmcp: The FastMCP server instance.
            path_params: Dictionary of path parameters captured from the ASGI request scope.
            **kwargs: Additional keyword arguments for Pydantic BaseModel initialization.
        """
        super().__init__(
            request_context=request_context,
            fastmcp=fastmcp,
            **kwargs
        )
        self.path_params = path_params if path_params is not None else {}
