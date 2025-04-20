from django.apps import AppConfig
from django.conf import settings
from django_mcp import mcp_app
from .loader import register_mcp_modules
from .log import logger, configure_logging

class MCPConfig(AppConfig):
    name = 'django_mcp'
    verbose_name = 'Django MCP'

    def apply_default_settings(self):
        default_settings = {
            'MCP_LOG_LEVEL': 'INFO',
            'MCP_LOG_TOOL_REGISTRATION': True,
            'MCP_SERVER_TITLE': 'MCP Server',
            'MCP_SERVER_INSTRUCTIONS': 'Provides MCP tools',
            'MCP_SERVER_VERSION': '0.1.0',
        }

        for key, value in default_settings.items():
            if not hasattr(settings, key):
                setattr(settings, key, value)

    def ready(self):
        # Add defaults to Django settings if not already set
        self.apply_default_settings()

        # Re-configure logging for the MCP app
        configure_logging()

        # Load MCP modules
        register_mcp_modules()
        tools = mcp_app._tool_manager.list_tools()
        if settings.MCP_LOG_TOOL_REGISTRATION:
            for tool in tools:
                logger.info(f"Registered MCP tool: {tool.name} - {tool.description}")
