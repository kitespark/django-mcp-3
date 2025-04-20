from mcp.server.fastmcp import FastMCP
from .log import logger
from .decorators import log_mcp_tool_calls

def patch_mcp_tool_decorator(mcp_app: FastMCP):
    original_tool_decorator_factory = mcp_app.tool

    def patched_tool_decorator_factory(*args, **kwargs):
        inner_sdk_decorator = original_tool_decorator_factory(*args, **kwargs)
        def combined_decorator(func):
            logged_func = log_mcp_tool_calls(func)
            return inner_sdk_decorator(logged_func)
        return combined_decorator

    mcp_app.tool = patched_tool_decorator_factory
    logger.info("Applied monkey patch to mcp_app.tool to automatically log tool calls. This can be disabled by setting MCP_PATCH_SDK_TOOL_LOGGING=False in settings.py.")
