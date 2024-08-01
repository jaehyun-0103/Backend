# chat/management/commands/initialize_vectorstores.py
from django.core.management.base import BaseCommand
import asyncio
from chat.consumers import initialize_global_vectorstore

class Command(BaseCommand):
    help = 'Initialize vectorstores'

    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        story_ids = ['1']  # 초기화할 story_id 목록

        async def init_vectorstores():
            for story_id in story_ids:
                await initialize_global_vectorstore(story_id)

        loop.run_until_complete(init_vectorstores())
        self.stdout.write(self.style.SUCCESS('Successfully initialized vectorstores'))