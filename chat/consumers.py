#chat/consumers.py
import json, logging
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI
from django.conf import settings
from django_redis import get_redis_connection
from langchain_community.docstore.wikipedia import Wikipedia
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

client = OpenAI(api_key=settings.OPENAI_API_KEY)
redis_conn = get_redis_connection("default")

# langchain을 이용한 Wikipedia 내용 가져오기
def get_wikipedia_content(url, max_length=10000):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    content = soup.find_all('p')
    text_content = ' '.join([para.text for para in content])
    # 최대 길이 제한
    if len(text_content) > max_length:
        text_content = text_content[:max_length]
    return text_content

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

        logger.info(f'WebSocket connected: Story ID {self.story_id}')

    # 비동기식으로 Websocket 연결 종료할 때 로직
    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        logger.info(f'WebSocket disconnected: Story ID {self.story_id}')

    #사용자가 JSON 형식으로 메시지를 보내면 호출
    async def receive(self, text_data):
        try:
            text_data_json = json.loads(text_data)
            user_message = text_data_json.get('message', '')

            if user_message:
                logger.info(f'Received message from user (Story ID {self.story_id}): {user_message}')

                gpt_response = await self.get_gpt_response(user_message)
                await self.send(text_data=json.dumps({
                    'message': gpt_response
                }))
        except json.JSONDecodeError:
            logger.error("Invalid JSON format received from client.")
            return

    async def get_gpt_response(self, user_message):
        logger.info(f'Generating GPT response for user message (Story ID {self.story_id}): {user_message}')
        # redis를 통해 캐시에 대화 내용을 저장하기 위한 로직
        cache_key = f'gptchat_{self.story_id}'
        chat_history = redis_conn.lrange(cache_key, 0, -1)

        if not chat_history:
            chat_history = []

        # 대화 기록을 구조화하여 메시지 리스트로 변환
        messages_history = []
        for item in chat_history:
            message = json.loads(item)
            messages_history.append({"role": message["role"], "content": message["content"]})

        # 사용자 메시지 추가
        messages_history.append({"role": "user", "content": user_message})

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
            # 파인튜닝 인식을 위한 인퍼런스
            studying_content_map = {
                '1': "넌 겸손한 이순신 장군님이 되어 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 장군의 말투로 하면 돼."
                # 파인튜닝 진행될 떄 마다 추가
                # '2': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '3': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '4': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '5': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '6': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '7': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '8': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '9': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '10': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
            }

            # Wikipedia url 가져오기
            wikipedia_url_map = {
                '1': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # 파인튜닝 진행될 떄 마다 추가
                # '2': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '3': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '4': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '5': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '6': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '7': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '8': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '9': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '10': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
            }

            if self.story_id in model_map:
                model = model_map[self.story_id]
                studying_content = studying_content_map[self.story_id]
                wikipedia_content = wikipedia_url_map[self.story_id]

                # 메시지 리스트가 길 경우 자르기
                while len(messages_history) > 50:
                    messages_history.pop(0)

                # "role"이 "user"일 때의 가장 최근 2개의 "content" 추출
                user_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "user"][-2:]

                # "role"이 "assistant"일 때의 가장 최근 2개의 "content" 추출
                assistant_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "assistant"][-2:]

                # 메시지 리스트 구성
                messages = [
                    # 파인튜닝된 정보 인퍼런스
                    {"role": "system",
                     "content": f"{studying_content}, 다음은 인물에 대한 정보야: {wikipedia_content} 인물의 말투가 일관되게 답변해줘."},
                    {"role": "user", "content": user_message},
                    # 캐시에 저장된 대화 내용 불러오기
                    {"role": "system", "content": f"다음은 너와 대화하는 'user'의 최근 대화 내용이야:{user_messages_history} 'user'가 이 내용에 대해 물으면 인물의 말투가 일관되게 답변해줘."},
                    {"role": "system", "content": f"다음은 너의 최근 대화 내용이야:{assistant_messages_history} 인물의 말투가 일관되게 답변해줘."},
                ]

                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )

                if response and response.choices and len(response.choices) > 0:
                    gpt_response = response.choices[0].message.content
                    messages_history.append({"role": "assistant", "content": gpt_response})
                    redis_conn.ltrim(cache_key, -6, -1)  # 최근 6개의 대화만 유지
                    redis_conn.rpush(cache_key, json.dumps({"role": "user", "content": user_message}))
                    redis_conn.rpush(cache_key, json.dumps({"role": "assistant", "content": gpt_response}))
                else:
                    gpt_response = "답변 생성이 불가능 합니다."

            #story_id를 할당하지 못했을 때 빈 객체 값으로 반환
            else:
                gpt_response = f"잘못된 story_id: {self.story_id}입니다."
                return gpt_response

        except KeyError as ke:
            print(f"OpenAI API 응답 처리 중 KeyError: {str(ke)}가 발생했습니다.")
            gpt_response = "GPT가 예상하지 못한 응답 형식입니다."

        except Exception as e:
            print(f"OpenAI API를 호출하는 중 Error: {str(e)}가 발생했습니다")
            gpt_response = f"GPT에서 응답 생성 중 오류가 발생했습니다: {str(e)}"

        return gpt_response

