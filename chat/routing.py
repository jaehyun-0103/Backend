#chat\routing.py
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/<int:story_id>/', ChatConsumer.as_asgi()),
]
