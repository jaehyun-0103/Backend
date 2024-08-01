# manage_vectorstore.py
import asyncio
from django.conf import settings
from django_redis import get_redis_connection
from .consumers import ChatConsumer

async def initialize_vectorstore():
    consumer = ChatConsumer()
    await consumer.initialize_vectorstore()
    return consumer.vectorstores

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    vectorstores = loop.run_until_complete(initialize_vectorstore())
    # 벡터스토어를 전역 변수로 설정하여 다른 모듈에서 접근 가능하도록 합니다.
    global_vectorstores = vectorstores
