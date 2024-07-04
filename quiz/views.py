from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from story.models import Story
from .models import Quiz
from result.models import Result
from user.models import User
from .serializers import QuizSerializer, UpdateResultSerializer

# Create your views here.
class GetQuizView(APIView):
    def get(self, request, user_id, story_id):
        user = get_object_or_404(User, pk=user_id)
        story = get_object_or_404(Story, pk=story_id)
        result = Result.objects.filter(user=user, story=story).first()

        if result:
            puzzle_cnt = result.puzzle_cnt
        else:
            puzzle_cnt = 0

        if puzzle_cnt == 0:
            quizzes = Quiz.objects.filter(story=story)[:5]
        elif puzzle_cnt == 1:
            quizzes = Quiz.objects.filter(story=story)[5:10]
        elif puzzle_cnt == 2:
            quizzes = Quiz.objects.filter(story=story)[10:15]
        elif puzzle_cnt == 3:
            quizzes = Quiz.objects.filter(story=story)[15:20]
        else:
            quizzes = Quiz.objects.filter(story=story)[:20]

        serializer = QuizSerializer(quizzes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateQuizResult(APIView):
    def put(self, request, user_id, story_id):
        user = get_object_or_404(User, pk=user_id)
        story = get_object_or_404(Story, pk=story_id)
        result = Result.objects.filter(user=user, story=story).first()

        if not result:
            return Response({"detail": "Result not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateResultSerializer(data=request.data)
        if serializer.is_valid():
            additional_correct_cnt = serializer.validated_data.get('correct_cnt', 0)
            if result.puzzle_cnt < 4:
                result.correct_cnt += additional_correct_cnt
                result.puzzle_cnt += 1
            result.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)