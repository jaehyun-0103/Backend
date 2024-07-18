#chat/consumers.py
import json, logging, requests, base64, bs4, asyncio
from channels.generic.websocket import AsyncWebsocketConsumer
from openai import OpenAI
from django.conf import settings
from django_redis import get_redis_connection
from langchain import hub
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain.chat_models import ChatOpenAI
from langchain_community.embeddings.fastembed import FastEmbedEmbeddings
from concurrent.futures import ThreadPoolExecutor
from functools import partial

logger = logging.getLogger(__name__)

# 파일 핸들러 추가
file_handler = logging.FileHandler('application.log')
file_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)

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

        logger.info(f'WebSocket connected: Story ID {self.story_id}')

        # 각 모델의 초기 인사, 파인튜닝이 되지 않은 경우 "아직 개발중인 모델입니다." 메시지 설정
        initial_message_map = {
            '1': "반갑소, 소인 이순신 장군이라 하오. 아직 대화할 준비가 안되었으니 잠시 기다려 주시면 감사하겠소.",
            '2': "아직 개발 진행 중인 모델입니다.",
            '3': "아직 개발 진행 중인 모델입니다.",
            '4': "아직 개발 진행 중인 모델입니다.",
            '5': "아직 개발 진행 중인 모델입니다.",
            '6': "아직 개발 진행 중인 모델입니다.",
            '7': "아직 개발 진행 중인 모델입니다.",
            '8': "아직 개발 진행 중인 모델입니다.",
        }

        # 초기 인사 메시지 설정
        if self.story_id in initial_message_map:
            initial_message = initial_message_map[self.story_id]

            # 클라이언트에게 초기 인사 메시지 전송
            await self.send(text_data=json.dumps({
                'message': initial_message
            }))

        # 벡터 스토어 생성 작업 비동기 실행
        await self.initialize_vectorstore()

    # 벡터 스토어 초기화 함수
    # 속도 증진을 위해 웹소켓 연결이 되었을 때 벡터스토어 생성까지 해둔다.
    async def initialize_vectorstore(self):
        try:
            # Wikipedia url 가져오기
            wikipedia_url_map = {
                '1': 'https://ko.wikipedia.org/wiki/이순신',
                # 파인튜닝 진행될 떄 마다 추가
                # '2': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '3': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '4': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '5': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '6': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '7': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
                # '8': get_wikipedia_content('https://ko.wikipedia.org/wiki/이순신'),
            }

            story_id = self.story_id

            # 단계 1: 문서 로드(Load Documents)
            # Wikipedia 내용을 로드하고, 청크로 나누고, 인덱싱합니다.
            async def load_documents(story_id):
                wikipedia_url = wikipedia_url_map[story_id]
                loader = WebBaseLoader(
                    web_paths=(wikipedia_url,),
                    bs_kwargs=dict(
                        parse_only=bs4.SoupStrainer(
                            "div",
                            attrs={"class": ["mw-content-ltr mw-parser-output"], "lang": ["ko"], "dir": ["ltr"]},
                        )
                    ),
                )
                docs = loader.load()
                return docs

            # 단계 2: 문서 분할(Split Documents)
            async def split_documents(docs):
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=50, chunk_overlap=5)
                splits = text_splitter.split_documents(docs)
                return splits

            # 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
            # 벡터스토어를 생성합니다.
            # 속도 개선을 위해 병렬로 처리
            def create_vectorstore_sync(splits):
                embeddings = FastEmbedEmbeddings()
                vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
                return vectorstore

            async def create_vectorstore(splits):
                loop = asyncio.get_event_loop()
                with ThreadPoolExecutor() as pool:
                    vectorstore = await loop.run_in_executor(pool, partial(create_vectorstore_sync, splits))
                return vectorstore

            # 문서 로드 비동기 실행
            docs_task = asyncio.create_task(load_documents(story_id))
            docs = await docs_task
            logger.info('문서 로드가 완료되었습니다.')

            # 문서 분할 비동기 실행
            splits_task = asyncio.create_task(split_documents(docs))
            splits = await splits_task
            logger.info('문서 분할이 완료되었습니다.')

            # 벡터스토어 생성 비동기 실행
            vectorstore_task = asyncio.create_task(create_vectorstore(splits))
            self.vectorstore = await vectorstore_task
            logger.info('벡터스토어 생성이 완료되었습니다.')

            # 각 모델의 대화 준비 완료 문구
            ready_message_map = {
                '1': "오래 기다리셨소, 기다리게 해서 미안하오. 이제야 대화할 준비가 다 되었구려. 무엇이 궁금하시오?",
                # 파인튜닝 진행될 떄 마다 추가
                # '2': "반갑소, 소인 이순신 장군이라 하오.",
                # '3': "반갑소, 소인 이순신 장군이라 하오.",
                # '4': "반갑소, 소인 이순신 장군이라 하오.",
                # '5': "반갑소, 소인 이순신 장군이라 하오.",
                # '6': "반갑소, 소인 이순신 장군이라 하오.",
                # '7': "반갑소, 소인 이순신 장군이라 하오.",
                # '8': "반갑소, 소인 이순신 장군이라 하오.",
            }

            # 준비 완료 메시지 설정
            if self.story_id in ready_message_map:
                ready_message = ready_message_map[self.story_id]

            # 클라이언트에게 준비 완료 메시지 전송
            await self.send(text_data=json.dumps({
                'message': ready_message
            }))

        except Exception as e:
            logger.error(f"벡터스토어 초기화 중 오류 발생: {str(e)}")

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

    #stt 처리 로직
    async def stt_process(self, speech_data):
        try:
            # Base64 디코딩
            audio_data = base64.b64decode(speech_data)

            # STT 처리를 위한 API 호출 (여기서는 네이버 STT API 예시)
            # 네이버 STT API 연동 코드
            client_id = settings.NAVER_CLIENT_ID
            client_secret = settings.NAVER_CLIENT_SECRET
            stt_url = 'https://naveropenapi.apigw.ntruss.com/recog/v1/stt'

            headers = {
                'Content-Type': 'application/octet-stream',
                'X-NCP-APIGW-API-KEY-ID': client_id,
                'X-NCP-APIGW-API-KEY': client_secret,
            }

            response = requests.post(stt_url, headers=headers, data=audio_data)
            if response.status_code == 200:
                stt_text = response.json()['text']
                return stt_text
            else:
                logger.error(f"STT API request failed with status code: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error during STT processing: {str(e)}")
            return None

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
                '1': "ft:gpt-3.5-turbo-1106:personal::9lFLU1pj",
                # 파인튜닝 진행될 떄 마다 추가
                # '2': "gpt-3.5-turbo-1106:personal2",
                # '3': "gpt-3.5-turbo-1106:personal3",
                # '4': "gpt-3.5-turbo-1106:personal4",
                # '5': "gpt-3.5-turbo-1106:personal5",
                # '6': "gpt-3.5-turbo-1106:personal6",
                # '7': "gpt-3.5-turbo-1106:personal7",
                # '8': "gpt-3.5-turbo-1106:personal8",
            }
            # 파인튜닝 인식을 위한 인퍼런스
            studying_content_map = {
                '1': "넌 이순신이야. 겸손한 이순신 장군님에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 장군의 말투로 하면 돼. 언어는 한글만 써."
                # 파인튜닝 진행될 떄 마다 추가
                # '2': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '3': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '4': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '5': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '6': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '7': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
                # '8': "넌 겸손한 이순신에 빙의해서 사용자와 대화를 진행할거야. 말투는 최대한 일관되게 조선시대 말투로 하면 돼.",
            }

            if self.story_id in model_map:
                model = model_map[self.story_id]
                studying_content = studying_content_map[self.story_id]

                # 메시지 리스트가 길 경우 자르기
                while len(messages_history) > 50:
                    messages_history.pop(0)

                # "role"이 "user"일 때의 가장 최근 2개의 "content" 추출
                user_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "user"][-2:]

                # "role"이 "assistant"일 때의 가장 최근 2개의 "content" 추출
                assistant_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "assistant"][-2:]

                 # 단계 4: 검색(Search)
                # 위키피디아에 포함되어 있는 정보를 검색하고 생성합니다.
                retriever = self.vectorstore.as_retriever(search_kwargs=dict(k=1))
                retrieved_docs = retriever.get_relevant_documents(user_message)
                logger.info(f"검색된 문서: {retrieved_docs}")

                # 단계 5: 프롬프트 생성(Create Prompt)
                # 프롬프트를 생성합니다.
                prompt = hub.pull("rlm/rag-prompt")
                logger.info('프롬포트 생성이 완료되었습니다.')

                def format_docs(docs):
                    # 검색한 문서 결과를 하나의 문단으로 합쳐줍니다.
                    return "\n\n".join(doc.page_content for doc in docs)
                logger.info('문서 합병이 완료되었습니다.')

                # 단계 6: LLM 모델 생성 (기존 모델 불러오기)
                llm = ChatOpenAI(openai_api_key=settings.OPENAI_API_KEY)
                logger.info('LLM 모델 생성이 완료되었습니다.')

                # 단계 7: 체인 생성(Create Chain)
                rag_chain = (
                        {"context": retriever | format_docs, "question": RunnablePassthrough()}
                        | prompt
                        | llm
                        | StrOutputParser()
                )
                logger.info('체인 생성이 완료되었습니다.')

               # 단계 8: 비동기로 체인 실행(Run Chain)
                rag_response = await asyncio.to_thread(rag_chain.invoke, user_message)
                logger.info('체인 실행이 완료되었습니다.')

                # 메시지 리스트 구성
                messages = [
                    # 파인튜닝된 정보 인퍼런스
                    {"role": "system", "content": f"{studying_content}"},
                    # 추가 파인튜닝 (메시지 기록, RAG 정보)
                    {"role": "system", "content": f"'role': 'user'의 최근 질문 내용이야.: {user_messages_history}, 'role': 'assitant'의 최근 답변 내용이야.: {assistant_messages_history}, RAG를 통해 얻어온 인물에 대한 자세한 정보야.: {rag_response} 이 정보들을 바탕으로 성격과 말투를 유지한 상태로 사용자의 물음에 정확한 대답을 해주면 돼. 너가 빙의한 인물 그 자체가 되는 것이기에 인물에 대한 3인칭 사용은 지양해. 그리고 동일한 답변을 반복하지 마. 또한, 사용자의 질문에 명확히 답변하고, 관련 없는 내용은 피해."},
                    # user message
                    {"role": "user", "content": user_message},
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
                gpt_response = f"아직 개발이 완료되지 않은 모델 story_id:{self.story_id}입니다."
                return gpt_response

        except KeyError as ke:
            logger.error(f"OpenAI API 응답 처리 중 KeyError: {str(ke)}가 발생했습니다.")
            gpt_response = "GPT가 예상하지 못한 응답 형식입니다."

        except Exception as e:
            logger.error(f"OpenAI API를 호출하는 중 Error: {str(e)}가 발생했습니다")
            gpt_response = f"GPT에서 응답 생성 중 오류가 발생했습니다: {str(e)}"

        return gpt_response
