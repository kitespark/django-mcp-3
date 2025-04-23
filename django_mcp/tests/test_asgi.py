"""Tests for django_mcp.asgi"""
import uuid
import pytest
from starlette.routing import Route, Mount
from starlette.applications import Starlette
from asgiref.typing import ASGIApplication

from django_mcp.asgi import _convert_django_path_to_starlette, mount_mcp_server
from django_mcp import mcp_app


@pytest.mark.parametrize(
    "django_path, expected_starlette_path",
    [
        ("/mcp", "/mcp"),
        ("/mcp/<slug:myslug>", "/mcp/{myslug:str}"),
        ("/items/<int:item_id>", "/items/{item_id:int}"),
        ("/users/<uuid:user_id>/profile", "/users/{user_id:uuid}/profile"),
        ("/path/<str:name>", "/path/{name:str}"),
        ("/files/<path:filepath>", "/files/{filepath:path}"),
        ("/prefix/<slug:s>/<int:i>/details", "/prefix/{s:str}/{i:int}/details"),
    ],
)
def test_convert_django_path_to_starlette(django_path, expected_starlette_path):
    """Test the conversion of Django-style path parameters to Starlette format."""
    assert _convert_django_path_to_starlette(django_path) == expected_starlette_path


async def dummy_http_app(scope, receive, send):
    """A minimal ASGI app for testing mounting."""
    pass


@pytest.mark.parametrize(
    "mcp_base_path_django, expected_sse_path_starlette, expected_messages_path_starlette",
    [
        # Note: Starlette Mount paths seem to lose the trailing slash unless it's just '/'
        ("/mcp", "/mcp/sse", "/mcp/messages"),
        ("/mcp/<slug:testslug>", "/mcp/{testslug:str}/sse", "/mcp/{testslug:str}/messages"),
        ("/api/v1/mcp/<uuid:conn_id>", "/api/v1/mcp/{conn_id:uuid}/sse", "/api/v1/mcp/{conn_id:uuid}/messages"),
    ],
)
def test_mount_mcp_server_route_generation(
    mcp_base_path_django,
    expected_sse_path_starlette,
    expected_messages_path_starlette,
    settings, # Use pytest-django settings fixture
):
    """Test that mount_mcp_server generates correct Starlette routes."""
    settings.MCP_SERVER_TITLE = "Test MCP"
    settings.MCP_SECRET_KEY = "test-secret"
    settings.MCP_ENABLE_SERVER_SENT_EVENTS = True
    settings.MCP_LOG_LEVEL = "INFO"
    settings.MCP_PATCH_SDK_TOOL_LOGGING = False  # Avoid patching for tests

    # Mount the server
    mounted_app: ASGIApplication = mount_mcp_server(
        django_http_app=dummy_http_app, mcp_base_path=mcp_base_path_django
    )

    # Check if the mounted app is a Starlette app
    assert isinstance(mounted_app, Starlette)

    sse_route_found = False
    messages_route_found = False
    actual_mount_paths = []

    for route in mounted_app.routes:
        if isinstance(route, Route):
            if route.path == expected_sse_path_starlette:
                sse_route_found = True
        elif isinstance(route, Mount):
            actual_mount_paths.append(route.path)
            if route.path == expected_messages_path_starlette:
                messages_route_found = True

    assert sse_route_found, f"SSE route {expected_sse_path_starlette} not found in routes"
    assert messages_route_found, f"Messages route {expected_messages_path_starlette} not found. Found Mount paths: {actual_mount_paths}"
