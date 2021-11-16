from channels.routing import ProtocolTypeRouter, URLRouter

from chat.routing import websocket_urlpatterns
from chat_backend.auth_middleware import JwtAuthMiddlewareStack

application = ProtocolTypeRouter({
    "websocket": JwtAuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})
