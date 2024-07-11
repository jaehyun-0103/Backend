#chat/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from story.models import Story
from user.models import User
from .models import Talk

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.story_id = self.scope['url_route']['kwargs']['story_id']
        self.room_group_name = f'story_{self.story_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        user_id = text_data_json['user_id']
        message = text_data_json['message']

        await self.save_talk(user_id, message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'user_id': user_id,
                'message': message
            }
        )

    @database_sync_to_async
    def save_talk(self, user_id, message):
        story = Story.objects.get(pk=self.story_id)
        user = User.objects.get(pk=user_id)
        Talk.objects.create(story=story, user=user, text=message)

    async def chat_message(self, event):
        user_id = event['user_id']
        message = event['message']

        await self.send(text_data=json.dumps({
            'user_id': user_id,
            'message': message
        }))
