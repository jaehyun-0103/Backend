from rest_framework import serializers
from .models import Story
from result.models import Result

class GreatsSerializer(serializers.ModelSerializer):
    greatId = serializers.IntegerField(source='id')
    puzzle_cnt = serializers.SerializerMethodField()
    class Meta:
        model = Story
        fields = ['greatId', 'name', 'silhouette_url', 'photo_url', 'saying', 'puzzle_cnt']

    def get_puzzle_cnt(self, obj):
        result = Result.objects.filter(story=obj).first()
        return result.puzzle_cnt if result else 0
