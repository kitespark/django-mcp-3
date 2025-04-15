# django-mcp

django-mcp adds MCP tool hosting to Django.

The [Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) specification is relatively new and has been changing rapidly. This library provides an abstraction layer between Django and the upstream [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) as well as utility functions and decorators to simplify development of MCP services in Django applications.

## Installation

Available on PyPI:

```bash
pip install django-mcp
```

## Usage

First, configure your Django ASGI application entrypoint `asgi.py` to mount the MCP server using `mount_mcp_server`:

```python
# asgi.py
import os
import django
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'my_project.settings')
django.setup()

from django_mcp import mount_mcp_server  # must come after django.setup()

django_http_app = get_asgi_application()

# for django ASGI:
application = mount_mcp_server(django_http_app=django_http_app, mcp_base_path='/mcp')

# for django-channels ASGI:
# from channels.routing import ProtocolTypeRouter
# application = ProtocolTypeRouter({
#     "http": mount_mcp_server(django_http_app=django_http_app, mcp_base_path='/mcp')
# })
```

Now the `mcp_app` FastMCP object can be accessed in your project files with the same interface as defined in the upstream [modelcontextprotocol/python-sdk](https://github.com/modelcontextprotocol/python-sdk) SDK.

```python
# my_app/tools.py
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

```python
# my_app/apps.py
import my_app.tools
```

To start your server:

```bash
uvicorn my_project.asgi:application --host 0.0.0.0 --port 8000
```

## MCP Inspector

Launch the inspector web app using the following command, then navigate to `http://127.0.0.1:6274`, change transport to SSE, and input your Django MCP URL like `http://localhost:8000/mcp/sse`.

```bash
npx @modelcontextprotocol/inspector

# Starting MCP inspector...
# ⚙️ Proxy server listening on port 6277
# 🔍 MCP Inspector is up and running at http://127.0.0.1:6274 🚀
```

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
