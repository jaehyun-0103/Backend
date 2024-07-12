import json
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI
from django.conf import settings
from django_redis import get_redis_connection

client = OpenAI(api_key=settings.OPENAI_API_KEY)
redis_conn = get_redis_connection("default")


class ChatConsumer(AsyncWebsocketConsumer):
    # 비동기식으로 Websocket 연결 되었을 때 로직
    async def connect(self):
        self.story_id = self.scope['url_route']['kwargs']['story_id']
        self.room_group_name = f'chat_{self.story_id}'
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    # 비동기식으로 Websocket 연결 종료할 때 로직
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

        # 첫 번째 메시지가 시스템 메시지인지 확인하여 추가
        # 첫 번째 메시지에 파인튜닝 정보 제공하여 gpt가 더 수월하게 파인튜닝 되도록 진행
        if not messages:
            if self.story_id == '1':
                initial_message = {"role": "system",
                                   "content": "너는 이순신이야. 이순신이 되어서 사용자가 물어보는 것에 대해 답변을 해주면 돼. 말투도 최대한 조선시대 사람처럼, 그리고 이순신처럼 얘기해주면 돼."}
                messages.append(initial_message)
                #파인튜닝 진행될 떄 마다 추가
            # if self.story_id == '2':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=2야"}
            #     messages.append(initial_message)
            # if self.story_id == '3':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=3야"}
            #     messages.append(initial_message)
            # if self.story_id == '4':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=4야"}
            #     messages.append(initial_message)
            # if self.story_id == '5':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=5야"}
            #     messages.append(initial_message)
            # if self.story_id == '6':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=6야"}
            #     messages.append(initial_message)
            # if self.story_id == '7':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=7야"}
            #     messages.append(initial_message)
            # if self.story_id == '8':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=8야"}
            #     messages.append(initial_message)
            # if self.story_id == '9':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=9야"}
            #     messages.append(initial_message)
            # if self.story_id == '10':
            #     initial_message = {"role": "system", "content": "너는 'story_id'=10야"}
            #     messages.append(initial_message)

        # 사용자 메시지 추가
        messages.append({"role": "user", "content": user_message})

        try:
            #story_id에 따른 모델을 선정하는 로직
            model_map = {
                '1': "ft:gpt-3.5-turbo-1106:personal::9kAzcucS",
                # 파인튜닝 진행될 떄 마다 추가
                # '2': "gpt-3.5-turbo-1106:personal2",
                # '3': "gpt-3.5-turbo-1106:personal3",
                # '4': "gpt-3.5-turbo-1106:personal4",
                # '5': "gpt-3.5-turbo-1106:personal5",
                # '6': "gpt-3.5-turbo-1106:personal6",
                # '7': "gpt-3.5-turbo-1106:personal7",
                # '8': "gpt-3.5-turbo-1106:personal8",
                # '9': "gpt-3.5-turbo-1106:personal9",
                # '10': "gpt-3.5-turbo-1106:personal10",
            }

            if self.story_id in model_map:
                model = model_map[self.story_id]
                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )

                if response and response.choices and len(response.choices) > 0:
                    gpt_response = response.choices[0].message.content
                    messages.append({"role": "assistant", "content": gpt_response})
                    redis_conn.ltrim(cache_key, -100, -1)  # 최근 100개의 대화만 유지
                    redis_conn.rpush(cache_key, json.dumps({"role": "user", "content": user_message}))
                    redis_conn.rpush(cache_key, json.dumps({"role": "assistant", "content": gpt_response}))
                else:
                    gpt_response = "답변 생성이 불가능 합니다."

            #story_id를 할당하지 못했을 때 빈 객체 값으로 반환
            else:
                gpt_response = f"Invalid story_id: {self.story_id}"
                return gpt_response

        except KeyError as ke:
            print(f"KeyError while processing OpenAI API response: {str(ke)}")
            gpt_response = "GPT가 예상하지 못한 응답 형식입니다."

        except Exception as e:
            print(f"Error while calling OpenAI API: {str(e)}")
            gpt_response = f"GPT에서 응답 생성 중 오류가 발생했습니다: {str(e)}"

        return gpt_response

