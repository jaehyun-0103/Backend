# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import GPTChatSerializer
from .consumers import ChatConsumer
from django.views.generic import TemplateView
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)

# 구현한 API 기능 확인할 수 있는 템플릿뷰
class ChatTemplateView(TemplateView):
    template_name = 'text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

# GPT와 대화하는 API뷰
class GPTChatView(APIView):
    serializer_class = GPTChatSerializer

    @swagger_auto_schema(
        operation_id="위인과 대화하기",
        operation_description="이 API는 웹소켓 통신을 사용하므로 별 다른 내용이 없음",
        responses={"200": GPTChatSerializer}
    )

    async def put(self, request, *args, **kwargs):
        gpt_message = request.data.get("message")
        story_id = self.kwargs['story_id']

        # 예시로 DEBUG 레벨의 로그 기록
        logger.debug(f'Received request for story_id {story_id} with message "{gpt_message}"')

        gpt_chat_content = await get_gpt_response(story_id, gpt_message)

        logger.info(f'Generated GPT response for story_id {story_id}')

        return Response({"message": "GPTChat 생성 완료", "gpt_chat_content": gpt_chat_content}, status=status.HTTP_201_CREATED)
