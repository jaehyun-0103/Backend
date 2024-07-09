from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Story
from .serializers import GreatsSerializer, GreatDetailSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class GreatsList(APIView):
    permission_classes = [permissions.AllowAny]

    @swagger_auto_schema(
        operation_id="위인 리스트 불러오기",
        operation_description="전체 위인 리스트 또는 선택한 나라 또는 분야의 위인 리스트 불러오기",
        responses={"200": GreatsSerializer},
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_QUERY,
                description="사용자 ID",
                type=openapi.TYPE_INTEGER,
                required=True
            ),
            openapi.Parameter(
                'nation',
                openapi.IN_QUERY,
                description="국가",
                type=openapi.TYPE_STRING
            ),
            openapi.Parameter(
                'field',
                openapi.IN_QUERY,
                description="분야",
                type=openapi.TYPE_STRING
            )
        ]
    )
    def get(self, request):
        logger.info("GreatsList GET request initiated.")
        user_id = request.data.get('user_id')
        nation = request.query_params.get('nation')
        field = request.query_params.get('field')

        logger.debug(f"Parameters received - user_id: {user_id}, nation: {nation}, field: {field}")

        if not user_id:
            logger.warning("User ID not provided.")
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Story.objects.filter(is_deleted=False)

        if nation:
            queryset = queryset.filter(nation=nation)
        if field:
            queryset = queryset.filter(field=field)

        serializer = GreatsSerializer(queryset, many=True, context={'user_id': user_id})
        logger.info("GreatsList GET request successful.")
        return Response(serializer.data)


class GreatDetail(APIView):
    @swagger_auto_schema(
        operation_id="선택한 위인 정보 불러오기",
        operation_description="위인 목록에서 선택한 위인의 정보 불러오기",
        responses={"200": GreatsSerializer},
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
        logger.info(f"GreatDetail GET request initiated for story_id: {story_id}")
        user_id = request.data.get('user_id')

        logger.debug(f"Parameters received - user_id: {user_id}")

        if not user_id:
            logger.warning("User ID not provided.")
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            story = Story.objects.get(pk=story_id, is_deleted=False)
        except Story.DoesNotExist:
            logger.error(f"Story with id {story_id} not found.")
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GreatDetailSerializer(story)
        logger.info(f"GreatDetail GET request successful for story_id: {story_id}")
        return Response(serializer.data, status=status.HTTP_200_OK)

class IncrementAccessCount(APIView):
    @swagger_auto_schema(
        operation_id="대화창 접속 수 증가하기",
        operation_description="Redis Cache를 통해 대화창에 접속한 횟수만큼 증가하기",
        responses={"200": "성공"},
        manual_parameters=[
            openapi.Parameter(
                'access_cnt',
                openapi.IN_QUERY,
                description="대화창 접속 여부",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ]
    )
    def put(self, request, story_id):
        logger.info(f"IncrementAccessCount PUT request initiated for story_id: {story_id}")

        # Get access_cnt from request data
        access_cnt = request.data.get('access_cnt')

        if access_cnt is None or not isinstance(access_cnt, bool):
            logger.warning("Invalid or missing access_cnt in request data.")
            return Response({"detail": "access_cnt가 제공되지 않았습니다."}, status=status.HTTP_400_BAD_REQUEST)

        if access_cnt:
            try:
                story = Story.objects.filter(pk=story_id, is_deleted=False).first()
                if story:
                    story.access_cnt += 1
                    story.save()
                    logger.info(f"Access count incremented successfully for story_id: {story_id}")
                    return Response({"detail": "성공"}, status=status.HTTP_200_OK)
                else:
                    logger.error(f"Story with id {story_id} not found.")
                    return Response({"detail": "해당 위인을 찾을 수 없습니다."}, status=status.HTTP_404_NOT_FOUND)
            except Exception as e:
                logger.error(f"Failed to increment access count for story_id {story_id}: {str(e)}")
                return Response({"detail": "접속 수 증가가 실패했습니다."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            logger.warning("access_cnt is false, no action taken.")
            return Response({"detail": "access_cnt가 올바르지 않습니다."}, status=status.HTTP_400_BAD_REQUEST)