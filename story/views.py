from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from .models import Story
from .serializers import GreatsSerializer, GreatDetailSerializer
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

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
        user_id = request.data.get('user_id')
        nation = request.query_params.get('nation')
        field = request.query_params.get('field')

        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        queryset = Story.objects.filter(is_deleted=False)

        if nation:
            queryset = queryset.filter(nation=nation)
        if field:
            queryset = queryset.filter(field=field)

        serializer = GreatsSerializer(queryset, many=True, context={'user_id': user_id})
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
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            story = Story.objects.get(pk=story_id, is_deleted=False)
        except Story.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GreatDetailSerializer(story)
        return Response(serializer.data, status=status.HTTP_200_OK)