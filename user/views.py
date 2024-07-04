from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer

@api_view(['POST'])
def create_user(request):
    if request.method == 'POST':
        data = request.data

        serializer = UserSerializer(data={
            'username': data.get('username'),
            'year': data.get('year'),
            'created_at': data.get('date')
        })
        if serializer.is_valid():
            user = serializer.save()
            return Response({'userID': user.id, 'username': user.username}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


