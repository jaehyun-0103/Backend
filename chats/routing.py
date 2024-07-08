from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/(?P<story_id>\d+)/talk/$', consumers.MyConsumer.as_asgi()),
]
