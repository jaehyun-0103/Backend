# chat/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Talk
from story.models import Story
from user.models import User
from .serializers import MessageSerializer
from django.views.generic import TemplateView

class ChatTemplateView(TemplateView):
    template_name = 'text.html'

class TalkView(APIView):
    serializer_class = MessageSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, story_id):
        talks = Talk.objects.filter(story_id=story_id)
        serializer = MessageSerializer(talks, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, story_id):
        user_id = request.data.get('user_id')
        text = request.data.get('text')

        if not user_id or not text:
            return Response({"detail": "사용자 ID 또는 텍스트가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            story = Story.objects.get(pk=story_id, is_deleted=False)
            user = User.objects.get(pk=user_id)
        except Story.DoesNotExist:
            return Response({"detail": "해당 이야기를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
        except User.DoesNotExist:
            return Response({"detail": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        talk = Talk.objects.create(story=story, user=user, text=text)
        serializer = MessageSerializer(talk)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
