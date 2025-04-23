"""
django_mcp/interop_django_fastapi.py

This module provides functions to:
- Convert Django path templates like `<int:pk>` into FastAPI-compatible `{pk:int}` style.
- Interpolate Starlette-style path templates (with or without type annotations)
  using URL parameters provided at runtime.

These helpers are used when mounting a FastAPI-based MCP application into a Django ASGI root.
"""

import re

# Regex for finding Django path converters
DJANGO_PATH_REGEX = re.compile(r"<([a-zA-Z_][a-zA-Z0-9_]*):([a-zA-Z_][a-zA-Z0-9_]*)>")


def _interpolate_starlette_path_with_url_params(path_template: str, path_params: dict) -> str:
    """
    Interpolates a Starlette-style path template with runtime URL parameters.

    This function removes any type annotations like `:str` from the path template
    and then applies `.format(**path_params)` to inject the values.

    Example:
        path_template: "/mcp/{slug:str}"
        path_params: {"slug": "a-pretty-uuid"}
        → "/mcp/a-pretty-uuid"

    Args:
        path_template: Starlette-style path string with optional type hints.
        path_params: Dictionary of parameters extracted from the request path.

    Returns:
        Fully interpolated path string with actual values.
    """
    # Remove type annotations like :str, :int, etc. to make it format-safe
    format_safe_path = re.sub(r":\w+", "", path_template)
    try:
        return format_safe_path.format(**path_params)
    except KeyError as e:
        raise KeyError(f"Missing key '{e}' in path_params {path_params} for template '{path_template}'") from e


def _convert_django_path_to_starlette(django_path: str) -> str:
    """
    Converts a Django-style path definition to a Starlette-compatible format.

    Example:
        django_path: "tools/<int:tool_id>/run"
        → "tools/{tool_id:int}/run"

    Args:
        django_path: A path string from Django's URL patterns using <type:name> syntax.

    Returns:
        A converted path string using Starlette-style {name:type} syntax.
    """
    def replace_converter(match):
        type_name = match.group(1)
        param_name = match.group(2)
        starlette_type = {
            "slug": "str",  # Starlette doesn't have a specific slug type, use str
            "str": "str",
            "int": "int",
            "uuid": "uuid",
            "path": "path",
        }.get(type_name, "str")  # Default to string if type is unknown
        return f"{{{param_name}:{starlette_type}}}"

    return DJANGO_PATH_REGEX.sub(replace_converter, django_path)
