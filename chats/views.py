from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from story.models import Story
from result.models import Result
from user.models import User
from .serializers import MessageSerializer

# 사용자 정의 예외 클래스, 예외 발생 시 즉각적인 HTTP 응답을 위해 사용
class ImmediateResponseException(Exception):
    # 예외 인스턴스를 생성할 때 HTTP 응답 객체를 받음
    def __init__(self, response):
        self.response = response
class TalkView(APIView):
    def post(self, request, story_id):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Story.objects.filter(is_deleted=False)

        serializer = MessageSerializer(queryset, many=True, context={'user_id': user_id})
        return Response(serializer.data)

