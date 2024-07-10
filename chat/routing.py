#chat\routing.py
from django.urls import path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    path('ws/<int:story_id>/talk/', ChatConsumer.as_asgi()),
]
