from django.shortcuts import render

from rest_framework import generics
from .models import Story
from .serializers import AllGreatsSerializer

class AllGreatsList(generics.ListAPIView):
    queryset = Story.objects.filter(is_deleted=False)
    serializer_class = AllGreatsSerializer