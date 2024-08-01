import asyncio
from chat.consumers import initialize_global_vectorstore

async def initialize_vectorstores():
    story_ids = ['1']  # 초기화할 story_id 목록
    for story_id in story_ids:
        await initialize_global_vectorstore(story_id)

def run_initialization():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(initialize_vectorstores())