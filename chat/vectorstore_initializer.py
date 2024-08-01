# chat/vectorstore_initializer.py
import asyncio
from django.conf import settings
from django_redis import get_redis_connection
from chat.consumers import initialize_global_vectorstore

redis_conn = get_redis_connection("default")

async def initialize_vectorstores():
    story_ids = ['1']  # 초기화할 story_id 목록
    for story_id in story_ids:
        await initialize_global_vectorstore(story_id)

def run_initialization():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(initialize_vectorstores())
