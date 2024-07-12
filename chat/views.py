import requests
from openai import OpenAI
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .serializers import GPTChatSerializer
from story.models import Story
from user.models import User
from django.views.generic import TemplateView
from django.shortcuts import get_object_or_404
from django.conf import settings
from backend.settings import OPENAI_API_KEY
from django.core.cache import cache

client = OpenAI(api_key=settings.OPENAI_API_KEY)

class ChatTemplateView(TemplateView):
    template_name = 'text.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class GPTChatView(APIView):
    serializer_class = GPTChatSerializer

    def put(self, request, *args, **kwargs):
        gpt_message = request.data.get("message")
        story_id = self.kwargs['story_id']

        gpt_chat_content = self.generate_gpt_chat(gpt_message)

        return Response({"message": "GPTChat 생성 완료", "gpt_chat_content": gpt_chat_content}, status=status.HTTP_201_CREATED)

    def generate_gpt_chat(self, gpt_message):
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "user", "content": gpt_message},
                    {"role": "system", "content": f"GPT said: {gpt_message}"},
                ],
            )

            if response and response.choices and len(response.choices) > 0:
                gpt_chat_content = response.choices[0].message.get('content', '')
            else:
                gpt_chat_content = "Sorry, I couldn't generate a response at the moment."

        except Exception as e:
            print(f"Error while calling OpenAI API: {str(e)}")
            gpt_chat_content = "Error while generating response from GPT."

        return gpt_chat_content
