from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema

import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


@swagger_auto_schema(
    method='post',
    operation_id="사용자의 정보 저장하기",
    operation_description="사용자의 이름과 출생연도 저장하기",
    request_body=UserSerializer,
    responses={"200": UserSerializer},
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
@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        logger.info("Create user request received.")
        data = request.data
        logger.debug(f"Request data: {data}")

        serializer = UserSerializer(data={
            'username': data.get('username'),
            'year': data.get('year'),
        })

        if serializer.is_valid():
            user = serializer.save()
            logger.info(f"User created successfully with ID: {user.id}")
            return Response({'userID': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)

        logger.warning(f"Validation errors: {serializer.errors}")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    else:
        logger.error("Unsupported request method.")
        return Response({'detail': 'Method not allowed.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
