# django-mcp

django-mcp adds MCP tool hosting to Django.

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) specification is relatively new and has been changing rapidly. This library provides an abstraction layer between Django and the upstream [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) as well as utility functions and decorators to simplify development of MCP services in Django applications.

## Installation

Available on PyPI:

```bash
pip install django-mcp
```

Add `'django_mcp'` to your `INSTALLED_APPS` setting like this:

```python
# settings.py
INSTALLED_APPS = [
    ...
    'django_mcp',
]
```

## Usage

To use this library, you need to mount the MCP ASGI application to a route in your existing Django ASGI application.

### ASGI setup

First, configure your Django ASGI application entrypoint `asgi.py` to mount the MCP server using `mount_mcp_server`:

```python
# asgi.py
import os
import django
from django.core.asgi import get_asgi_application

# new import
from django_mcp import mount_mcp_server

# configure settings module path
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')

# initialize django
django.setup()

# get the django http application
django_http_app = get_asgi_application()

# combine the django asgi and mcp asgi applications
application = mount_mcp_server(django_http_app=django_http_app, mcp_base_path='/mcp')

# for django-channels ASGI:
# from channels.routing import ProtocolTypeRouter
# application = ProtocolTypeRouter({
#     "http": mount_mcp_server(django_http_app=django_http_app, mcp_base_path='/mcp')
# })
```

To start your server:

```bash
uvicorn my_project.asgi:application --host 0.0.0.0 --port 8000
```

Now the `mcp_app` FastMCP object can be accessed in your project files with the same interface as defined in the upstream [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) SDK.

### MCP decorators

This library exports `mcp_app` which corresponds to the upstream [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) `FastMCP` object instance. You can use any of the upstream API decorators like `@mcp_app.tool` to define your tools, prompts, resources, etc.

```python
from django_mcp import mcp_app as mcp

@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """Get a personalized greeting"""
    return f"Hello, {name}!"
```

## Configuration

This library allows customization through Django settings. The following settings can be defined in your project's `settings.py`:

| key                       | description                                        | default             |
| ------------------------- | -------------------------------------------------- | ------------------- |
| `MCP_SERVER_TITLE`        | Sets the title of the MCP server                   | `'MCP Server'`      |
| `MCP_SERVER_INSTRUCTIONS` | Sets the instructions provided by the MCP server   | `'Provides MCP tools'` |
| `MCP_SERVER_VERSION`      | Sets the version of the MCP server                 | `'0.1.0'`           |

If a setting is not found in your project's `settings.py`, the default value will be used.

---


## MCP Inspector

This library includes a convenient management command to run the MCP Inspector tool against your Django application.

Start the inspector by running the following command in your project's root directory (where `manage.py` is located):

```bash
python manage.py mcp_inspector [url]
```

Replace `[url]` with the URL of your running MCP server, typically `http://localhost:8000/mcp/sse`. If you omit the URL, it defaults to `http://127.0.0.1:8000/mcp/sse`.

The command will start the inspector and output the URL (usually `http://127.0.0.1:6274`) where you can access it in your web browser.

---

## Future roadmap

* Streamable HTTP transport
* Authentication and authorization

---

## Development

```bash
# Set up virtualenv (replace path)
export VIRTUAL_ENV=./.venv/django-mcp
uv venv --python 3.8 --link-mode copy ${VIRTUAL_ENV}
uv sync
```

---

## License

This project is licensed un the MIT License.

By submitting a pull request, you agree that any contributions will be licensed under the MIT License, unless explicitly stated otherwise.
