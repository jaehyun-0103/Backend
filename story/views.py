from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Story
from .serializers import GreatsSerializer, GreatDetailSerializer

class GreatsList(APIView):
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

        serializer = GreatsSerializer(queryset, many=True)
        return Response(serializer.data)

class GreatDetail(APIView):
    def get(self, request, pk):
        user_id = request.data.get('user_id')

        if not user_id:
            return Response({"detail": "User ID not provided."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            story = Story.objects.get(pk=pk, is_deleted=False)
        except Story.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = GreatDetailSerializer(story)
        return Response(serializer.data, status=status.HTTP_200_OK)