from channels.routing import ProtocolTypeRouter, URLRouter

from chat.routing import websocket_urlpatterns
from chat_backend.ws_middleware import WebsocketMiddlewareStack

application = ProtocolTypeRouter({
    "websocket": WebsocketMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    )
})
