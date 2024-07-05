from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Story
from .serializers import GreatsSerializer

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