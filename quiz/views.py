from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from story.models import Story
from .models import Quiz
from result.models import Result
from user.models import User
from .serializers import QuizSerializer, UpdateResultSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GetQuizView(APIView):
    @swagger_auto_schema(
        operation_id="해당 위인의 퀴즈 불러오기",
        operation_description="0개 : 1~5번, 1개: 6~10번 2개: 11~15번 3개: 16~20번 4개: 모든 문제(1~20번)",
        responses={"200": QuizSerializer},
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="사용자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def get(self, request, story_id):
        user_id = request.data.get('user_id')

        if user_id:
            logger.info(f"GetQuizView called with user_id={user_id} and story_id={story_id}")
        else:
            logger.error("User ID not provided")
            return Response({"detail": "사용자 ID가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
            logger.info(f"User {user} found")
        except User.DoesNotExist:
            logger.error("User not found")
            return Response({"detail": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            story = Story.objects.get(pk=story_id)
            logger.info(f"Story {story} found")
        except Story.DoesNotExist:
            logger.error("Story not found")
            return Response({"detail": "해당 위인을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        result, created = Result.objects.get_or_create(user=user, story=story, defaults={'puzzle_cnt': 0, 'correct_cnt': 0})
        if created:
            logger.info(f"New Result created for user_id={user_id} and story_id={story_id}")
        logger.info(f"Result for user_id={user_id} and story_id={story_id}: {result}")

        puzzle_cnt = result.puzzle_cnt
        logger.info(f"Puzzle count: {puzzle_cnt}")

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
    @swagger_auto_schema(
        operation_id="퀴즈 퍼즐 저장하기",
        operation_description="맞춘 퀴즈 문제 수를 저장하고, 얻은 퍼즐 개수 업데이트 하기",
        responses={"200": UpdateResultSerializer},
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="사용자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def put(self, request, story_id):
        user_id = request.data.get('user_id')

        if user_id:
            logger.info(f"UpdateQuizResult called with user_id={user_id} and story_id={story_id}")
        else:
            logger.error("User ID not provided")
            return Response({"detail": "사용자 ID가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(pk=user_id)
            logger.info(f"User {user} found")
        except User.DoesNotExist:
            logger.error("User not found")
            return Response({"detail": "해당 사용자를 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        try:
            story = Story.objects.get(pk=story_id)
            logger.info(f"Story {story} found")
        except Story.DoesNotExist:
            logger.error("Story not found")
            return Response({"detail": "해당 위인을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        result = Result.objects.filter(user=user, story=story).first()
        logger.info(f"Result for user_id={user_id} and story_id={story_id}: {result}")

        if not result:
            logger.error("Result not found")
            return Response({"detail": "퀴즈 풀이 내역을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        serializer = UpdateResultSerializer(data=request.data)
        if serializer.is_valid():
            additional_correct_cnt = serializer.validated_data.get('correct_cnt')
            logger.info(f"Additional correct count: {additional_correct_cnt}")

            if result.puzzle_cnt < 4:
                result.correct_cnt += additional_correct_cnt
                result.puzzle_cnt += 1
                logger.info(f"Updated result: correct_cnt={result.correct_cnt}, puzzle_cnt={result.puzzle_cnt}")
            result.save()
            return Response({"detail": "성공"}, status=status.HTTP_200_OK)
        else:
            logger.error(f"Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
