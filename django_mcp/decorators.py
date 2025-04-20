import functools
import inspect
import logging

from .log import logger


def log_mcp_tool_calls(func):
    """
    Decorator to log MCP tool calls, arguments, results, and exceptions.

    Logs entry with arguments at DEBUG level.
    Logs successful return value at DEBUG level.
    Logs exceptions at WARNING level with traceback and re-raises the exception.
    Handles both synchronous and asynchronous functions.
    """
    @functools.wraps(func)
    async def async_wrapper(*args, **kwargs):
        tool_name = func.__name__
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling async MCP tool '{tool_name}' with args: {args}, kwargs: {kwargs}")
        try:
            result = await func(*args, **kwargs)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Async MCP tool '{tool_name}' returned: {result}")
            return result
        except Exception as e:
            logger.warning(f"Exception in async MCP tool '{tool_name}': {e}", exc_info=True)
            raise e

    @functools.wraps(func)
    def sync_wrapper(*args, **kwargs):
        tool_name = func.__name__
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(f"Calling sync MCP tool '{tool_name}' with args: {args}, kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            if logger.isEnabledFor(logging.DEBUG):
                logger.debug(f"Sync MCP tool '{tool_name}' returned: {result}")
            return result
        except Exception as e:
            logger.warning(f"Exception in sync MCP tool '{tool_name}': {e}", exc_info=True)
            raise e

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    else:
        return sync_wrapper
