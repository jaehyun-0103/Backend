from channels.routing import ProtocolTypeRouter, URLRouter
from django.urls import path
from chats.consumers import MyConsumer

application = ProtocolTypeRouter({ 'http': get_asgi_application(), 'websocket': AuthMiddlewareStack( URLRouter([ path('ws/chats/{int:story_id}/talk/', MyConsumer.as_asgi()), ]) ), })