from django.urls import path

from chats import consumers

websocket_urlpatterns = [
    path("ws/<int:story_id>/talk", consumers.MyConsumer.as_asgi()),
]