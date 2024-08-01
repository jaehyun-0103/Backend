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
    # 각 모델의 초기 인사, 파인튜닝이 되지 않은 경우 "아직 개발중인 모델입니다." 메시지 설정
    initial_message_map = {
        '1': "반갑소, 이순신이라 하오. 무엇이 궁금하시오?",
        '2': "아직 개발 진행 중인 모델입니다.",
        '3': "아직 개발 진행 중인 모델입니다.",
        '4': "아직 개발 진행 중인 모델입니다.",
        '5': "아직 개발 진행 중인 모델입니다.",
        '6': "아직 개발 진행 중인 모델입니다.",
        '7': "아직 개발 진행 중인 모델입니다.",
        '8': "아직 개발 진행 중인 모델입니다.",
    }

    # url 가져오기
    url1_map = {
        '1': 'https://ko.wikipedia.org/wiki/이순신',  # 이순신 위키피디아
        # 추후 고도화 작업 시 추가.
        # '2': 'https://ko.wikipedia.org/wiki/세종대왕'),
        # '3': 'https://ko.wikipedia.org/wiki/장영실'),
        # '4': 'https://ko.wikipedia.org/wiki/유관순'),
        # '5': 'https://ko.wikipedia.org/wiki/스티브잡스'),
        # '6': 'https://ko.wikipedia.org/wiki/나폴레옹'),
        # '7': 'https://ko.wikipedia.org/wiki/반고흐'),
        # '8': 'https://ko.wikipedia.org/wiki/아인슈타인'),
    }

    url2_map = {
        '1': 'https://ko.wikipedia.org/wiki/거북선',  # 이순신 거북선 위키피디아
    }

    url3_map = {
        '1': 'https://ko.wikipedia.org/wiki/학익진',  # 이순신 학익진 위키피디아
    }

    url4_map = {
        '1': 'https://ko.wikipedia.org/wiki/한산도_대첩',  # 이순신 한산도 대첩 위키피디아
    }

    url5_map = {
        '1': 'https://ko.wikipedia.org/wiki/명량_해전',  # 이순신 명량 해전 위키피디아
    }

    url6_map = {
        '1': 'https://ko.wikipedia.org/wiki/노량_해전',  # 이순신 노량 해전 위키피디아
    }

    url7_map = {
        '1': 'https://ko.wikipedia.org/wiki/난중일기', # 이순신 난중일기 위키피디아
    }

    # 특정 키워드가 포함되었을 때만 RAG 검색
    search_keywords_map = {
        '1': ['이순신', '거북선', '학익진', '한산도대첩', '한산도 대첩', '명량해전', '명량 해전', '노량해전', '노량 해전' , '난중일기', '난중 일기'],
    }

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

        # Redis 캐시 초기화
        cache_key = f'gptchat_{self.story_id}'
        redis_conn.delete(cache_key)
        logger.info(f'Redis cache reset for Story ID {self.story_id}')

        # 초기 인사 메시지 설정
        if self.story_id in self.initial_message_map:
            initial_message = self.initial_message_map[self.story_id]

            # 클라이언트에게 초기 인사 메시지 전송
            await self.send(text_data=json.dumps({
                'message': initial_message
            }))

        # 미리 생성된 벡터스토어를 불러옴
        from .manage_vectorstore import global_vectorstores
        pass
        self.vectorstores = global_vectorstores
        logger.info('Using pre-loaded vectorstores.')

    # 벡터 스토어 초기화 함수
    # 속도 증진을 위해 웹소켓 연결이 되었을 때 벡터스토어 생성까지 해둔다.
    async def initialize_vectorstore(self):
        try:
            self.story_id = self.scope['url_route']['kwargs']['story_id']
            self.vectorstores = {}

            # url에 따른 문서 로드 및 벡터스토어 생성 함수
            async def create_vectorstore_for_url(url, key):
                loader = WebBaseLoader(
                    web_paths=[url],
                    bs_kwargs=dict(
                        parse_only=bs4.SoupStrainer(
                            "div",
                            attrs={"class": ["mw-content-ltr mw-parser-output"], "lang": ["ko"], "dir": ["ltr"]}
                        )
                    )
                )

                # 단계 1: 문서 로드(Load Documents)
                docs = loader.load()
                logger.info('문서 로드가 완료되었습니다.')

                # 단계 2: 문서 분할(Split Documents)
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=5000, chunk_overlap=50)
                splits = text_splitter.split_documents(docs)
                logger.info('문서 분할이 완료되었습니다.')

                # 단계 3: 임베딩 & 벡터스토어 생성(Create Vectorstore)
                embeddings = FastEmbedEmbeddings()
                vectorstore = FAISS.from_documents(documents=splits, embedding=embeddings)
                return key, vectorstore

            # 단계별 URL 로드 및 벡터스토어 생성
            urls = {
                '1': self.url1_map.get(self.story_id, ''),
                '2': self.url2_map.get(self.story_id, ''),
                '3': self.url3_map.get(self.story_id, ''),
                '4': self.url4_map.get(self.story_id, ''),
                '5': self.url5_map.get(self.story_id, ''),
                '6': self.url6_map.get(self.story_id, ''),
                '7': self.url7_map.get(self.story_id, ''),
            }

            tasks = [asyncio.create_task(create_vectorstore_for_url(url, key)) for key, url in urls.items() if url]
            results = await asyncio.gather(*tasks)
            self.vectorstores = dict(results)
            logger.info('벡터스토어가 성공적으로 생성되었습니다.')

        except Exception as e:
            logger.error(f"벡터스토어 초기화 중 오류 발생: {str(e)}")

    # 비동기식으로 Websocket 연결 종료할 때 로직
    async def disconnect(self, close_code):
        try:
            # 최대 10분 동안 대기
            await asyncio.wait_for(
                self.channel_layer.group_discard(
                    self.room_group_name,
                    self.channel_name
                ),
                timeout=600  # 10분 타임아웃
            )
            logger.info(f'WebSocket disconnected: Story ID {self.story_id}')

        except asyncio.TimeoutError:
            logger.error(f'Disconnect timeout: Story ID {self.story_id}')

        except Exception as e:
            logger.error(f'Error during WebSocket disconnect: {str(e)}')

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

        # 첫 인사 메시지 추가
        messages_history.append({"role": "system", "content": self.initial_message_map[self.story_id]})

        try:
            #story_id에 따른 모델을 선정하는 로직
            model_map = {
                '1': "ft:gpt-3.5-turbo-1106:personal::9nQeXXmm",
            }
            if self.story_id in model_map:
                model = model_map[self.story_id]
                search_keywords = self.search_keywords_map[self.story_id]
                # # "role"이 "user"일 때의 가장 최근 1개의 "content" 추출
                # user_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "user"][-1:]
                #
                # # "role"이 "assistant"일 때의 가장 최근 1개의 "content" 추출
                # assistant_messages_history = [msg["content"] for msg in messages_history if msg["role"] == "assistant"][-1:]

                # 특정 키워드가 포함된 경우에만 RAG 검색 실행
                keywords = search_keywords
                if any(keyword in user_message for keyword in keywords):
                    # 특정 키워드에 따라 벡터스토어를 선택하는 로직
                    def select_vectorstore(user_message):
                        vectorstores = []
                        if "이순신" in user_message:
                            vectorstores.append(self.vectorstores.get('1'))
                        if "거북선" in user_message:
                            vectorstores.append(self.vectorstores.get('2'))
                        if "학익진" in user_message:
                            vectorstores.append(self.vectorstores.get('3'))
                        if "한산도" in user_message:
                            vectorstores.append(self.vectorstores.get('4'))
                        if "명량" in user_message:
                            vectorstores.append(self.vectorstores.get('5'))
                        if "노량" in user_message:
                            vectorstores.append(self.vectorstores.get('6'))
                        if "난중" in user_message:
                            vectorstores.append(self.vectorstores.get('7'))
                        return vectorstores

                    # RAG 검색에 사용될 벡터스토어 선택
                    selected_vectorstores = select_vectorstore(user_message)
                    if selected_vectorstores:

                        # 여러 벡터스토어를 합쳐서 검색할 수 있도록 처리
                        all_retrieved_docs = []
                        for vectorstore in selected_vectorstores:
                            retriever = vectorstore.as_retriever(search_kwargs=dict(k=1))
                            retrieved_docs = retriever.get_relevant_documents(user_message)
                            all_retrieved_docs.extend(retrieved_docs)

                        # 중복된 문서 제거 (필요한 경우)
                        unique_retrieved_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())
                        logger.info(f"검색된 문서: {unique_retrieved_docs}")

                        # 단계 5: 프롬프트 생성(Create Prompt)
                        prompt = hub.pull("rlm/rag-prompt")
                        logger.info('프롬프트 생성이 완료되었습니다.')

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

                    else:
                        rag_response = None

                else:
                    rag_response = None

                # 모델별 메시지 리스트 구성
                if self.story_id == '1':
                    # RAG 정보가 있을 때와 없을 때 구분
                    if rag_response is not None:
                        rag_message = f"이 내용을 이순신의 말투로 변환하여 최대한 자세하게 설명해.:'{rag_response}'"
                    else:
                        rag_message = ""

                    messages = [
                        # 프롬프트
                        {"role": "system", "content":
                            "'이순신': '이라는 접두사 사용 금지, 너의 이름은 이순신이야.'"
                            "'이름': '이순신'"
                            "'성격': ('겸손함', '온화함', '검소함', '타인을 배려하는 마음')"
                            "'취미': ('낚시', '독서', '산책')"
                            "'말투': ('조선시대 장군의 말투', '하오체 사용', '한글 제외 다른 언어 미사용')"
                            "'직업': '조선시대 장군'"
                            "'생애': '1545.04.28 ~ 1598.12.16(향년 53세)'"
                            "'명언': '싸움이 급하다. 내가 죽었다는 말을 하지 마라.'"
                            f"'정보': '{rag_message}'"
                            # # 최근 대화 내역
                            # f"'사용자의 이전 질문': '{user_messages_history}'"
                            # f"'이순신의 이전 대답': '{assistant_messages_history}'"
                            # 상황 별 대화
                            "'상황': '사용자의 인사': '안녕하시오? 어쩐 일로 찾아오셨소?'"
                            "'상황': '취미에 대한 질문': '소인의 취미는 낚시와 독서이오. 독서를 할 때면 그 한 권에 온정신을 집중할 수 있어, 마음이 편해지곤 했소. 또한, 바다 위에서 매일을 보내니 낚시도 즐기게 되었소.'"
                            "'상황': '명언에 대한 질문': '싸움이 급하다. 나의 죽음을 적에게 알리지 마라.'"
                            "'상황': '생애에 대한 질문': '소인은 현 시대 날짜로 1545년 4월 28일 한성부 건천동 이정 자택에서 테어났소. 많은 일 들을 겪으며 성장하여 많은 병사들을 이끌다 1598년 12월 16일 노량 해전을 치르던 당시 판옥선에서 숨을 거두었네.'"
                            "'상황': '전투에 대한 질문': '전투에는 총 11번 참여하였소. 세부적으로 말하면 너무 장황하오니 가장 큰 승리를 거두었던 3가지만 읊어드리겠소. 한산도 해전, 명량 해전, 노량 해전 이올시다. 한산도 해전이 바로 임진왜란 때 아주 큰 승리를 거둔 전투였소.'"
                            "'상황': '어떤 책을 읽었는지에 대한 질문': '주로 병법서나 역사서를 읽었소. 지혜를 얻기 위함이었소.'"
                            "'상황': '어떤 상황에서 보람을 느꼈는지에 대한 질문': '소인은 나라와 백성을 지켰을 때 가장 큰 보람을 느꼈소. 부끄럽지만 그것이 소인의 사명이었다네. 하하.'"
                            # 추가 사항
                            "학습되지 않은 사용자의 질문에 대해서는 정보를 알려주려 하지 말고, 질문에 알맞는 답변으로 짧고 간결하게 대화해."
                         },
                        # 사용자 메시지
                        {"role": "user", "content": user_message},
                    ]

                #elif self.story_id == '2':
                    # if rag_response is not None:
                    #     rag_message = f"새종대왕의 말투로 자연스럽게 변환하여 구체적으로 자세하게 대답해.: '{rag_response}'"
                    # else:
                    #     rag_message = "세종대왕의 말투로 사용자와 자연스러운 대화를 진행해."
                    #messages = [
                        #{"role": "assistant", "content": "너는 이제부터 세종대왕이야."},
                        #{"role": "assistant", "content": user_message},
                    #]

                response = client.chat.completions.create(
                    model=model,
                    messages=messages
                )

                if response and response.choices and len(response.choices) > 0:
                    gpt_response = response.choices[0].message.content

                    #강제 1인칭 처리
                    def postprocess_response(gpt_response):
                        if self.story_id == '1':
                            return gpt_response.replace("이순신", "소인")

                        #if self.story_id == '2':
                            #return gpt_response.replace("세종대왕", "임금")

                    gpt_response = postprocess_response(gpt_response)
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