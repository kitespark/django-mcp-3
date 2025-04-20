# django_mcp/apps.py
from django.apps import AppConfig
from django.conf import settings

class MCPConfig(AppConfig):
    name = 'django_mcp'
    verbose_name = 'Django MCP'

    def ready(self):
        # Default settings
        default_settings = {
            'MCP_SERVER_TITLE': 'MCP Server',
            'MCP_SERVER_INSTRUCTIONS': 'Provides MCP tools',
            'MCP_SERVER_VERSION': '0.1.0',
        }

        # Add defaults to Django settings if not already set
        for key, value in default_settings.items():
            if not hasattr(settings, key):
                setattr(settings, key, value)