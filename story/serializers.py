from rest_framework import serializers
from .models import Story

class AllGreatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Story
        fields = ['greatId', 'name', 'silhouette_url', 'photo_url', 'saying', 'puzzleCnt']