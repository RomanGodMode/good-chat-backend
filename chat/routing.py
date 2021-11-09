from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import re_path

from chat import consumers
from chat.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'chat/$', consumers.ChatConsumer.as_asgi())
]
