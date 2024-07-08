from channels.generic.websocket import AsyncJsonWebsocketConsumer
from channels.db import database_sync_to_async
from .models import Talk
from story.models import Story
from users.models import User

class MyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.story_id = self.scope['url_route']['kwargs']['story_id']  # URL 경로에서 위인 ID를 추출

            if not await self.check_story_exists(self.story_id):  # 위인이 존재하는지 확인
                raise ValueError('위인이 존재하지 않습니다.')

            await self.accept()  # WebSocket 연결을 수락

        except ValueError as e:  # 값 오류가 있을 경우, 오류 메시지를 보내고 연결을 종료
            await self.send_json({'error': str(e)})
            await self.close()

    async def disconnect(self, close_code):
            pass

    async def receive(self, text_data):
        # 클라이언트로부터 메시지를 받았을 때 실행되는 코드
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        await self.send(text_data=json.dumps({
            'message': message
        }))

    async def send_message(self, message):
        await self.send(text_data=json.dumps({
            'message': message
        }))