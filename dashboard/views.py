
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from user.models import User
from story.models import Story
from result.models import Result
from django.db.models import Count, Sum
from datetime import date, timedelta

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class DateVisitsAPIView(APIView):
    @swagger_auto_schema(
        operation_id="날짜별 방문자 수 통계내기",
        operation_description="Redis Cache를 통해 최근 일주일 간 방문자 수 통계내기",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'date': openapi.Schema(type=openapi.TYPE_STRING, format='date', description='방문일'),
                            'visit_total': openapi.Schema(type=openapi.TYPE_STRING, description='방문자 수')
                        }
                    )
                )
            )
        }
    )
    def get(self, request, format=None):
        try:
            logger.info("DateVisitsAPIView GET request initiated.")

            today = date.today()
            date_range = [today - timedelta(days=i) for i in range(7)]

            visit_data = User.objects.filter(
                created_at__date__in=date_range
            ).values('created_at__date').annotate(
                visit_total=Count('id')
            ).order_by('created_at__date')

            if not visit_data:
                logger.warning("No users found in the date range.")
                return Response({"detail": "해당 기간 내에 방문자가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            response_data = [
                {
                    'date': visit['created_at__date'].strftime('%Y-%m-%d'),
                    'visit_total': str(visit['visit_total'])
                }
                for visit in visit_data
            ]

            logger.info("DateVisitsAPIView GET request successful.")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in DateVisitsAPIView GET request: {str(e)}")
            return Response({"detail": "서버에서 데이터를 가져오는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AgeVisitsAPIView(APIView):
    @swagger_auto_schema(
        operation_id="나이별 가입자 수 통계내기",
        operation_description="Redis Cache를 통해 나이별 가입자 수 통계내기",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'age': openapi.Schema(type=openapi.TYPE_STRING, description='나이'),
                            'visit_total': openapi.Schema(type=openapi.TYPE_STRING, description='방문자 수')
                        }
                    )
                )
            )
        }
    )
    def get(self, request, format=None):
        try:
            logger.info("AgeVisitsAPIView GET request initiated.")

            current_year = date.today().year
            all_users = User.objects.all()

            if not all_users:
                logger.warning("No users found.")
                return Response({"detail": "사용자 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

            sorted_years = sorted([current_year - user.year + 1 for user in all_users])

            age_counts = {}
            for year in sorted_years:
                age_counts[year] = age_counts.get(year, 0) + 1

            response_data = [
                {
                    'age': str(year),
                    'visit_total': str(count)
                }
                for year, count in age_counts.items()
            ]

            logger.info("AgeVisitsAPIView GET request successful.")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in AgeVisitsAPIView GET request: {str(e)}")
            return Response({"detail": "서버에서 데이터를 가져오는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ChatVisitsAPIView(APIView):
    @swagger_auto_schema(
        operation_id="위인별 대화창 접속 수 통계내기",
        operation_description="Redis Cache를 통해 위인별 대화창 접속 수 통계내기",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='위인 이름'),
                            'access_cnt': openapi.Schema(type=openapi.TYPE_STRING, description='접속 수')
                        }
                    )
                )
            )
        }
    )
    def get(self, request, format=None):
        try:
            logger.info("ChatVisitsAPIView GET request initiated.")

            chats_data = Story.objects.values('name', 'access_cnt')

            response_data = [
                {
                    'name': chat['name'],
                    'access_cnt': str(chat['access_cnt'])
                }
                for chat in chats_data
            ]

            logger.info("ChatVisitsAPIView GET request successful.")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in ChatVisitsAPIView GET request: {str(e)}")
            return Response({"detail": "서버에서 데이터를 가져오는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CorrectRateAPIView(APIView):
    @swagger_auto_schema(
        operation_id="위인별 정답률 통계내기",
        operation_description="Redis Cache를 통해 위인별 정답률을 백분율로 통계내기",
        responses={
            200: openapi.Response(
                description="성공",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'name': openapi.Schema(type=openapi.TYPE_STRING, description='위인 이름'),
                            'correct_rate': openapi.Schema(type=openapi.TYPE_STRING, description='정답률(백분율)')
                        }
                    )
                )
            )
        }
    )
    def get(self, request, format=None):
        try:
            logger.info("CorrectRateAPIView GET request initiated.")

            all_story_ids = Story.objects.values_list('id', flat=True)

            results = Result.objects.values('story').annotate(
                total_correct=Sum('correct_cnt'),
                total_puzzles=Sum('puzzle_cnt')
            ).order_by('story')

            response_data = []
            for story_id in all_story_ids:
                result = results.filter(story=story_id).first()

                if result:
                    if result['total_puzzles'] > 0:
                        correct_rate = (result['total_correct'] / (result['total_puzzles'] * 5)) * 100
                    else:
                        correct_rate = 0

                    story_name = Story.objects.get(id=story_id).name

                    response_data.append({
                        'name': story_name,
                        'correct_rate': f"{correct_rate:.0f}%"
                    })
                else:
                    story_name = Story.objects.get(id=story_id).name
                    response_data.append({
                        'name': story_name,
                        'correct_rate': None
                    })

            logger.info("CorrectRateAPIView GET request successful.")
            return Response(response_data)

        except Exception as e:
            logger.error(f"Error in CorrectRateAPIView GET request: {str(e)}")
            return Response({"detail": "서버에서 데이터를 가져오는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
