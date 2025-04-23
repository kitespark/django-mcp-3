"""
django_mcp/log.py
"""
import logging
import sys
from django.conf import settings

logger = logging.getLogger('django_mcp')

def configure_logging():
    """
    Configure logging for django_mcp.
    Always set up a console handler unless django_mcp is configured in settings.LOGGING.

    Can be safely called multiple times with the same result.
    """
    # Check if the django_mcp logger is configured in settings
    try:
        if hasattr(settings, 'LOGGING'):
            loggers = settings.LOGGING.get('loggers', {})
            if 'django_mcp' in loggers:
                # Project has explicitly configured our logger, don't override
                return logger
    except Exception:
        # If settings aren't fully loaded yet, we continue
        pass

    # Get log level from django.conf.settings or default to INFO
    try:
        log_level = getattr(settings, 'MCP_LOG_LEVEL', 'INFO')
    except Exception:
        log_level = 'INFO'

    # Remove all existing handlers
    for handler in list(logger.handlers):
        logger.removeHandler(handler)

    # Add NullHandler to prevent "No handler found" warnings
    logger.addHandler(logging.NullHandler())

    # Add console handler
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter('%(name)s [%(levelname)s] %(message)s')
    console.setFormatter(formatter)

    # Add handler to logger and set level
    logger.setLevel(log_level)
    logger.addHandler(console)

    # Prevent propagation to avoid duplicate logs
    logger.propagate = False

    return logger

# Initial configuration - may be called again later
logger = configure_logging()