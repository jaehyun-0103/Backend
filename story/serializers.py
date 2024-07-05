from rest_framework import serializers
from .models import Story
from result.models import Result

class GreatsSerializer(serializers.ModelSerializer):
    greatId = serializers.IntegerField(source='id')
    puzzleCnt = serializers.SerializerMethodField()
    class Meta:
        model = Story
        fields = ['greatId', 'name', 'silhouette_url', 'photo_url', 'saying', 'puzzleCnt']

    def get_puzzleCnt(self, obj):
        result = Result.objects.filter(story=obj).first()
        return result.puzzleCnt if result else 0
