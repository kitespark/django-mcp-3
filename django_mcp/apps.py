from django.apps import AppConfig
from django.conf import settings
from django_mcp import mcp_app
# Import the decorator to be applied
from .decorators import log_mcp_tool_calls
from .loader import register_mcp_modules
from .log import logger, configure_logging
from .mcp_sdk_patches import patch_mcp_tool_decorator

class MCPConfig(AppConfig):
    name = 'django_mcp'
    verbose_name = 'Django MCP'

    def apply_default_settings(self):
        default_settings = {
            'MCP_LOG_LEVEL': 'INFO',
            'MCP_LOG_TOOL_REGISTRATION': True,
            'MCP_LOG_TOOL_DESCRIPTIONS': False,
            'MCP_SERVER_TITLE': 'MCP Server',
            'MCP_SERVER_INSTRUCTIONS': 'Provides MCP tools',
            'MCP_SERVER_VERSION': '0.1.0',
            'MCP_DIRS': [],
            'MCP_PATCH_SDK_TOOL_LOGGING': True,
        }

        for key, value in default_settings.items():
            if not hasattr(settings, key):
                setattr(settings, key, value)

    def ready(self):
        # Add defaults to Django settings if not already set
        self.apply_default_settings()

        # Re-configure logging for the MCP app
        configure_logging()

        # Apply monkey patches
        if settings.MCP_PATCH_SDK_TOOL_LOGGING:
            patch_mcp_tool_decorator(mcp_app)

        # Load MCP modules
        register_mcp_modules()
        tools = mcp_app._tool_manager.list_tools()
        if settings.MCP_LOG_TOOL_REGISTRATION:
            for tool in tools:
                description = f" - {tool.description}" if settings.MCP_LOG_TOOL_DESCRIPTIONS else ""
                logger.info(f"Registered MCP tool: {tool.name}{description}")

