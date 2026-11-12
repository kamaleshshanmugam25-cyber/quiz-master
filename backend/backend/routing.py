from channels.routing import URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

import quiz.routing


websocket_application = AllowedHostsOriginValidator(
    URLRouter(quiz.routing.websocket_urlpatterns)
)
