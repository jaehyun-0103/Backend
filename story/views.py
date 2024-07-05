from rest_framework import generics
from .models import Story
from .serializers import GreatsSerializer

class GreatsList(generics.ListAPIView):
    serializer_class = GreatsSerializer

    def get_queryset(self):
        queryset = Story.objects.filter(is_deleted=False)
        nation = self.request.GET.get('nation')
        field = self.request.GET.get('field')

        if nation:
            queryset = queryset.filter(nation=nation)
        if field:
            queryset = queryset.filter(field=field)

        return queryset