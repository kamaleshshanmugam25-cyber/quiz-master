"""
ASGI config for backend project.
Handles both HTTP (Django) and WebSocket (Django Channels) protocols.
"""

import os
from django.core.asgi import get_asgi_application
from channels.security.websocket import AllowedHostsOriginValidator
from channels.routing import ProtocolTypeRouter, URLRouter

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Initialise Django — must happen before any app imports
django_asgi_app = get_asgi_application()

# Import routing AFTER Django is initialised
import quiz.routing  # noqa: E402

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    # No AuthMiddlewareStack — app uses Token auth, not session auth.
    # Phones and cross-origin clients connect without session cookies.
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            quiz.routing.websocket_urlpatterns
        )
    ),
})
