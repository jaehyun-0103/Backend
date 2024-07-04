from rest_framework import serializers
from .models import Quiz

class QuizSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quiz
        fields = ['question', 'answer', 'explanation']

class UpdateResultSerializer(serializers.Serializer):
    correct_cnt = serializers.IntegerField()