# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .consumers import ChatConsumer
from django.views.generic import TemplateView
from drf_yasg.utils import swagger_auto_schema
import logging, asyncio

logger = logging.getLogger(__name__)

# 구현한 API 기능 확인할 수 있는 템플릿뷰
class ChatTemplateView(TemplateView):
    template_name = 'text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context