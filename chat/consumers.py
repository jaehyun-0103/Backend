import json
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI
from django.conf import settings
from django_redis import get_redis_connection

client = OpenAI(api_key=settings.OPENAI_API_KEY)
redis_conn = get_redis_connection("default")  # Redis 연결을 가져옵니다


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.story_id = self.scope['url_route']['kwargs']['story_id']
        self.room_group_name = f'chat_{self.story_id}'
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
        try:
            text_data_json = json.loads(text_data)
            user_message = text_data_json.get('message', '')

            if user_message:
                gpt_response = await self.get_gpt_response(user_message)
                await self.send(text_data=json.dumps({
                    'message': gpt_response
                }))
        except json.JSONDecodeError:
            print("Invalid JSON format received from client.")
            return

    async def get_gpt_response(self, user_message):
        cache_key = f'gptchat_{self.story_id}'
        chat_history = redis_conn.lrange(cache_key, 0, -1)

        if not chat_history:
            chat_history = []

        # 대화 기록을 구조화하여 메시지 리스트로 변환
        messages = []
        for item in chat_history:
            message = json.loads(item)
            messages.append({"role": message["role"], "content": message["content"]})

        # 새 메시지를 대화 기록에 추가
        messages.append({"role": "user", "content": user_message})

        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=messages,
            )

            if response and response.choices and len(response.choices) > 0:
                gpt_response = response.choices[0].message.content
                messages.append({"role": "assistant", "content": gpt_response})
                redis_conn.ltrim(cache_key, -100, -1)  # 최근 100개의 대화만 유지
                redis_conn.rpush(cache_key, json.dumps({"role": "user", "content": user_message}))
                redis_conn.rpush(cache_key, json.dumps({"role": "assistant", "content": gpt_response}))
            else:
                gpt_response = "Sorry, I couldn't generate a response at the moment."

            if not gpt_response:
                gpt_response = "Empty response from GPT model."

        except KeyError as ke:
            print(f"KeyError while processing OpenAI API response: {str(ke)}")
            gpt_response = "Error: Unexpected response format from GPT."

        except Exception as e:
            print(f"Error while calling OpenAI API: {str(e)}")
            gpt_response = f"Error while generating response from GPT: {str(e)}"

        return gpt_response
