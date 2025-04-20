import importlib
import importlib.machinery
import importlib.util
import os
import sys
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import module_has_submodule

from .log import logger


def load_mcp_dirs():
    dirs = settings.MCP_DIRS
    if not dirs:
        return

    for entry in dirs:
        base = Path(entry)
        if not base.is_absolute():
            base = Path(settings.BASE_DIR) / base
        if not base.exists():
            logger.warning(f"Skipping non‑existent MCP dir: {base}")
            continue

        for py in base.rglob("*.py"):
            if py.name == "__init__.py":
                continue
            module_name = f"mcp_dirs.{py.stem}"
            try:
                loader = importlib.machinery.SourceFileLoader(module_name, str(py))
                spec = importlib.util.spec_from_loader(module_name, loader)
                mod = importlib.util.module_from_spec(spec)
                loader.exec_module(mod)
                sys.modules[module_name] = mod
                logger.debug(f"Imported MCP file: {py}")
            except Exception as e:
                logger.error(f"Failed to import {py}: {e}", exc_info=True)


def autodiscover_mcp_modules():
    for app_config in apps.get_app_configs():
        if module_has_submodule(app_config.module, "mcp"):
            mcp_module_name = f"{app_config.name}.mcp"
            try:
                importlib.import_module(mcp_module_name)
                logger.debug(f"Imported MCP module: {mcp_module_name}")
            except Exception as e:
                logger.error(f"Failed to import MCP module {mcp_module_name}: {e}", exc_info=True)


def register_mcp_modules():
    autodiscover_mcp_modules()
    load_mcp_dirs()
