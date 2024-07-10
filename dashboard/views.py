from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django_redis import get_redis_connection
import json

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

            redis_conn = get_redis_connection("default")
            redis_key = f"dashboard:date:visits"
            logger.debug(f"Fetching data from Redis with key: {redis_key}")
            cached_data = redis_conn.get(redis_key)

            if cached_data:
                visit_data = json.loads(cached_data)
                logger.info("Cached data found for date visits.")
                return Response(visit_data, status=status.HTTP_200_OK)
            else:
                logger.warning("No cached data found for date visits.")
                return Response({"detail": "캐싱된 날짜별 방문자 수 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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

            redis_conn = get_redis_connection("default")
            redis_key = f"dashboard:age:visits"
            logger.debug(f"Fetching data from Redis with key: {redis_key}")
            cached_data = redis_conn.get(redis_key)

            if cached_data:
                visit_data = json.loads(cached_data)
                logger.info("Cached data found for age visits.")
                return Response(visit_data, status=status.HTTP_200_OK)
            else:
                logger.warning("No cached data found for age visits.")
                return Response({"detail": "캐싱된 나이별 가입자 수 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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

            redis_conn = get_redis_connection("default")
            redis_key = f"dashboard:chat:visits"
            logger.debug(f"Fetching data from Redis with key: {redis_key}")
            cached_data = redis_conn.get(redis_key)

            if cached_data:
                visit_data = json.loads(cached_data)
                logger.info("Cached data found for chat visits.")
                return Response(visit_data, status=status.HTTP_200_OK)
            else:
                logger.warning("No cached data found for chat visits.")
                return Response({"detail": "캐싱된 위인별 대화창 접속 수 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

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

            redis_conn = get_redis_connection("default")
            redis_key = f"dashboard:correct:rate"
            logger.debug(f"Fetching data from Redis with key: {redis_key}")
            cached_data = redis_conn.get(redis_key)

            if cached_data:
                visit_data = json.loads(cached_data)
                logger.info("Cached data found for correct rate.")
                return Response(visit_data, status=status.HTTP_200_OK)
            else:
                logger.warning("No cached data found for correct rate.")
                return Response({"detail": "캐싱된 위인별 정답률 데이터가 없습니다."}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error in CorrectRateAPIView GET request: {str(e)}")
            return Response({"detail": "서버에서 데이터를 가져오는 중 오류가 발생했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
