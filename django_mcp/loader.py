import importlib
import os
import sys
from pathlib import Path

from django.apps import apps
from django.utils.module_loading import module_has_submodule


def autodiscover_mcp_modules():
    """
    Search for and import MCP modules from all installed Django apps.

    This function looks for either:
    - An 'mcp.py' file directly in the app package
    - An 'mcp/__init__.py' file (mcp as a subpackage)
    """
    for app_config in apps.get_app_configs():
        app_path = Path(app_config.path)
        app_package = app_config.name

        # Check for mcp.py file
        mcp_module_name = f"{app_package}.mcp"
        mcp_path = app_path / "mcp.py"

        # Check for mcp/__init__.py (mcp as a package)
        mcp_package_path = app_path / "mcp" / "__init__.py"

        # Try importing the module if either file exists
        if mcp_path.exists() or mcp_package_path.exists():
            try:
                importlib.import_module(mcp_module_name)
            except ImportError as e:
                # Check if the error is actually from the MCP module itself
                # or from an import inside the MCP module
                if not module_has_submodule(sys.modules[app_package], 'mcp'):
                    # The module doesn't exist, so ignore the error
                    continue
                # The module exists but there was an import error inside it, so re-raise
                raise


def register_mcp_modules():
    autodiscover_mcp_modules()
