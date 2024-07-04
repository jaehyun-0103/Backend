from rest_framework import serializers
from .models import Story

class AllGreatsSerializer(serializers.ModelSerializer):
    greatId = serializers.IntegerField(source='id')

    class Meta:
        model = Story
        fields = ['greatId', 'name', 'silhouette_url', 'photo_url', 'saying', 'puzzleCnt']
