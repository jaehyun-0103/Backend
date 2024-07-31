# chat/routing.py
from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r'api/ws/chat/(?P<story_id>\w+)/$', ChatConsumer.as_asgi()),
]
